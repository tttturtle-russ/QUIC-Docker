// SPDX-License-Identifier: BSD-2-Clause
//
// Copyright (c) 2016-2017, NetApp, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
//    this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <sys/param.h>

#include <ev.h>
#include <picotls.h>
#include <quant/quant.h>
#include <warpcore/warpcore.h>

#include "conn.h"
#include "diet.h"
#include "frame.h"
#include "quic.h"
#include "recovery.h"
#include "stream.h"
#include "tls.h"


struct ev_loop;

static const ev_tstamp kFixedTimeout = 30.0;

uint32_t rtxable_pkts_outstanding(struct q_conn * const c)
{
    uint32_t cnt = 0;
    struct pkt_meta * p;
    splay_foreach (p, pm_nr_splay, &c->rec.sent_pkts)
        if (is_rtxable(p) && !p->is_acked)
            cnt++;
    return cnt;
}


static void __attribute__((nonnull)) set_ld_alarm(struct q_conn * const c) {
    // 使用固定的30秒超时时间
    c->rec.ld_alarm.repeat = kFixedTimeout;
    ev_timer_again(loop, &c->rec.ld_alarm);
}


static void __attribute__((nonnull)) detect_lost_pkts(struct q_conn * const c) {
    const ev_tstamp now = ev_now(loop);
    uint64_t largest_lost_packet = 0;
    struct pkt_meta *p, *nxt;

    for (p = splay_min(pm_nr_splay, &c->rec.sent_pkts); p && p->nr < c->rec.lg_acked; p = nxt) {
        nxt = splay_next(pm_nr_splay, &c->rec.sent_pkts, p);
        if (!p->is_acked && (now - p->tx_t > kFixedTimeout)) {
            warn(WRN, "pkt " FMT_PNR " considered lost", p->nr);
            if (is_rtxable(p)) {
                c->rec.in_flight -= p->tx_len;
                warn(INF, "in_flight -%u = %" PRIu64, p->tx_len, c->rec.in_flight);
            }
            largest_lost_packet = MAX(largest_lost_packet, p->nr);
            splay_remove(pm_nr_splay, &c->rec.sent_pkts, p);
        }
    }

    if (c->rec.rec_end < largest_lost_packet) {
        c->rec.rec_end = c->rec.lg_sent;
        c->rec.cwnd = MAX(c->rec.cwnd * kLossReductionFactor, kMinimumWindow);
        c->rec.ssthresh = c->rec.cwnd;
    }
}



static void __attribute__((nonnull))
on_ld_alarm(struct ev_loop * const loop, ev_timer * const w, int e) {
    struct q_conn * const c = w->data;

    if (c->state < CONN_STAT_ESTB) {
        warn(INF, "handshake RTX #%u on %s conn " FMT_CID, c->rec.hshake_cnt, conn_type(c), c->id);
        tx(c, true, 0);
        c->rec.hshake_cnt++;
    } else {
        warn(INF, "RTO alarm #%u on %s conn " FMT_CID, c->rec.rto_cnt, conn_type(c), c->id);
        if (c->rec.rto_cnt == 0) {
            c->rec.lg_sent_before_rto = c->rec.lg_sent;
        }
        tx(c, true, 2); // 进行重传
        c->rec.rto_cnt++;
    }

    set_ld_alarm(c); // 重新设置定时器
}



static void __attribute__((nonnull))
track_acked_pkts(struct q_conn * const c, const uint64_t ack)
{
    diet_remove(&c->recv, ack);
}


static void __attribute__((nonnull)) update_rtt(struct q_conn * const c)
{
    // 将srtt和rttvar固定设置为30秒和一部分的30秒
    c->rec.srtt = 30.0;  // 固定srtt为30秒
    c->rec.rttvar = 0.0; // 可以选择一个固定的较小值，这里假设为30秒的1/4

    warn(INF, "srtt = %f, rttvar = %f on %s conn " FMT_CID, c->rec.srtt,
         c->rec.rttvar, conn_type(c), c->id);
}



void on_pkt_sent(struct q_conn * const c, struct w_iov * const v)
{
    // sent_packets[packet_number] updated in enc_pkt()
    const ev_tstamp now = ev_now(loop);

    /* c->rec.last_sent_t = */ meta(v).tx_t = now;
    if (c->state != CONN_STAT_VERS_REJ)
        // don't track version negotiation responses
        splay_insert(pm_nr_splay, &c->rec.sent_pkts, &meta(v));

    if (is_rtxable(&meta(v))) {
        c->rec.in_flight += meta(v).tx_len; // OnPacketSentCC
        warn(INF, "in_flight +%u = %" PRIu64, meta(v).tx_len, c->rec.in_flight);
        set_ld_alarm(c);
    }
}


void on_ack_rx_1(struct q_conn * const c,
                 const uint64_t ack,
                 const uint16_t ack_delay)
{
    // if the largest ACKed is newly ACKed, update the RTT
    if (c->rec.lg_acked >= ack)
        return;

    c->rec.lg_acked = ack;
    struct w_iov * const v = find_sent_pkt(c, ack);
    ensure(v, "found ACKed pkt " FMT_PNR, ack);
    c->rec.latest_rtt = ev_now(loop) - meta(v).tx_t;
    if (c->rec.latest_rtt > ack_delay)
        c->rec.latest_rtt -= ack_delay;
    warn(INF, "latest_rtt %f", c->rec.latest_rtt);
    update_rtt(c);
}


void on_ack_rx_2(struct q_conn * const c)
{
    detect_lost_pkts(c);
    set_ld_alarm(c);
}


void on_pkt_acked(struct q_conn * const c, const uint64_t ack)
{
    struct w_iov * const v = find_sent_pkt(c, ack);
    if (!v) {
        warn(DBG, "got ACK for pkt " FMT_PNR " (%" PRIx64 ") with no metadata",
             ack, ack);
        return;
    }

    // only act on first-time ACKs
    if (meta(v).is_acked)
        warn(WRN, "repeated ACK for " FMT_PNR " (%" PRIx64 ")", ack, ack);
    else
        warn(NTE, "first ACK for " FMT_PNR " (%" PRIx64 ")", ack, ack);
    meta(v).is_acked = true;

    // If a packet sent prior to RTO was ACKed, then the RTO was spurious.
    // Otherwise, inform congestion control.
    if (c->rec.rto_cnt > 0 && ack > c->rec.lg_sent_before_rto) {
        c->rec.cwnd = kMinimumWindow; // OnRetransmissionTimeoutVerified
        warn(INF, "cwnd %u", c->rec.cwnd);
    }
    c->rec.hshake_cnt = c->rec.tlp_cnt = c->rec.rto_cnt = 0;
    splay_remove(pm_nr_splay, &c->rec.sent_pkts, &meta(v));

    if (rtxable_pkts_outstanding(c) == 0)
        maybe_api_return(q_close, c);

    // stop ACKing packets that were contained in the ACK frame of this
    // packet
    if (meta(v).ack_header_pos) {
        warn(DBG,
             "decoding ACK info from pkt " FMT_PNR " (%" PRIx64 ") from pos %u",
             ack, ack, meta(v).ack_header_pos);
        adj_iov_to_start(v);
        dec_ack_frame(c, v, meta(v).ack_header_pos, 0, &track_acked_pkts, 0);
        adj_iov_to_data(v);
        warn(DBG, "done decoding ACK info from pkt (%" PRIx64 ") from pos %u",
             ack, ack, meta(v).ack_header_pos);
    } else
        warn(DBG, "pkt " FMT_PNR " (%" PRIx64 ") did not contain an ACK frame",
             ack, ack);

    // OnPacketAckedCC
    if (is_rtxable(&meta(v))) {
        c->rec.in_flight -= meta(v).tx_len;
        warn(INF, "in_flight -%u = %" PRIu64, meta(v).tx_len, c->rec.in_flight);
    }

    if (ack >= c->rec.rec_end) {
        if (c->rec.cwnd < c->rec.ssthresh)
            c->rec.cwnd += meta(v).tx_len;
        else
            c->rec.cwnd += kDefaultMss * meta(v).tx_len / c->rec.cwnd;
        warn(INF, "cwnd %" PRIu64, c->rec.cwnd);
    }

    // check if a q_write is done
    if (meta(v).is_rtxed == false) {
        struct q_stream * const s = meta(v).str;
        if (s && ++s->out_ack_cnt == sq_len(&s->out))
            // all packets are ACKed
            maybe_api_return(q_write, s);
    }

    if (!is_rtxable(&meta(v))) {
        splay_remove(pm_nr_splay, &c->rec.sent_pkts, &meta(v));
        q_free_iov(v);
    }
}


struct w_iov * find_sent_pkt(struct q_conn * const c, const uint64_t nr)
{
    struct pkt_meta which = {.nr = nr};
    const struct pkt_meta * const p =
        splay_find(pm_nr_splay, &c->rec.sent_pkts, &which);
    return p ? w_iov(w_engine(c->sock), pm_idx(p)) : 0;
}


void rec_init(struct q_conn * const c)
{
    // we don't need to init variables to zero

    c->rec.ld_alarm.data = c;
    ev_init(&c->rec.ld_alarm, on_ld_alarm);

    if (c->use_time_loss_det) {
        c->rec.reorder_thresh = UINT64_MAX;
        c->rec.reorder_fract = kTimeReorderingFraction;
    } else {
        c->rec.reorder_thresh = kReorderingThreshold;
        c->rec.reorder_fract = HUGE_VAL;
    }
    splay_init(&c->rec.sent_pkts);

    tls_ctx.random_bytes(&c->rec.lg_sent, sizeof(uint32_t));
    c->rec.cwnd = kInitialWindow;
    c->rec.ssthresh = UINT64_MAX;
}
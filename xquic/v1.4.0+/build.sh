# get XQUIC source code
# git clone https://github.com/alibaba/xquic.git
cd xquic

# get and build BabaSSL
git clone -b 8.3-stable https://github.com/Tongsuo-Project/Tongsuo.git ./third_party/babassl
cd ./third_party/babassl/
./config --prefix=/usr/local/babassl
make -j
SSL_TYPE_STR="babassl"
SSL_PATH_STR="${PWD}"
SSL_INC_PATH_STR="${PWD}/include"
SSL_LIB_PATH_STR="${PWD}/libssl.a;${PWD}/libcrypto.a"
cd -

# build XQUIC with BabaSSL
git submodule update --init --recursive
mkdir -p build; cd build
cmake -DGCOV=on -DCMAKE_BUILD_TYPE=Debug -DXQC_ENABLE_TESTING=1 -DXQC_SUPPORT_SENDMMSG_BUILD=1 -DXQC_ENABLE_EVENT_LOG=1 -DXQC_ENABLE_BBR2=1 -DXQC_DISABLE_RENO=0 -DSSL_TYPE=${SSL_TYPE_STR} -DSSL_PATH=${SSL_PATH_STR} -DSSL_INC_PATH=${SSL_INC_PATH_STR} -DSSL_LIB_PATH=${SSL_LIB_PATH_STR} ..
make -j
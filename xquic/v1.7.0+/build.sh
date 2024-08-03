cd xquic

# 修改 xquic/tests/test_server.c 文件中的第1608行
# sed -i '1608s/#define TIMEOUT 10/#define TIMEOUT 30/' ./tests/test_server.c

# 编译 BabaSSL(Tongsuo)
git clone -b 8.3-stable https://github.com/Tongsuo-Project/Tongsuo.git ./third_party/babassl
cd ./third_party/babassl/
./config --prefix=/usr/local/babassl
make -j
SSL_TYPE_STR="babassl"
SSL_PATH_STR="${PWD}"
cd -

# 使用 BabaSSL（Tongsuo） 编译 XQUIC
# 选择BabaSSL编译XQUIC时，会默认从/usr/local/babassl寻找头文件、依赖库，如果BabaSSL在其
# 他位置，可以通过SSL_PATH指定位置。
# 在编译测试程序时，依赖了libevent、CUnit，默认会从系统安装路径下寻找，如果用户部署在特定位置
# 下，可以通过-DCUNIT_DIR、-DLIBEVENT_DIR指定目录。
git submodule update --init --recursive
mkdir -p build; cd build
cmake -DGCOV=on -DCMAKE_BUILD_TYPE=Debug -DXQC_ENABLE_TESTING=1 -DXQC_SUPPORT_SENDMMSG_BUILD=1 -DXQC_ENABLE_EVENT_LOG=1 -DXQC_ENABLE_BBR2=1 -DXQC_ENABLE_RENO=1 -DSSL_TYPE=${SSL_TYPE_STR} -DSSL_PATH=${SSL_PATH_STR} ..

# 如果CMake发生错误，则结束编译
if [ $? -ne 0 ]; then
    echo "cmake failed"
    exit 1
fi

make -j
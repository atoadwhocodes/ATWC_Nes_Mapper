#include "ATWC1.h"
#include <fstream>
class Demo:public ATWC1{public:
 std::vector<uint8_t> data;
 Demo(const char* f){std::ifstream in(f,std::ios::binary);data.assign(std::istreambuf_iterator<char>(in),{});_chrRom=data.data();_chrRomSize=data.size();InitMapper();live=true;}
 using ATWC1::WriteRegister;using ATWC1::ReadRegister;using ATWC1::MapperReadVram;
};
extern "C" {
void* make(const char* f){return new Demo(f);}
void put(void* p,int a,int v){static_cast<Demo*>(p)->ppu[a&16383]=v;}
void reg(void* p,int a,int v){static_cast<Demo*>(p)->WriteRegister(a,v);}
int getreg(void* p,int a){return static_cast<Demo*>(p)->ReadRegister(a);}
int fetch(void* p,int a){return static_cast<Demo*>(p)->MapperReadVram(a,MemoryOperationType::PpuRenderingRead);}
void destroy(void* p){delete static_cast<Demo*>(p);}
}

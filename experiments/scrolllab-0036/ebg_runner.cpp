#include "pch.h"
#include "Shared/Emulator.h"
#include "Shared/EmulatorLock.h"
#include "Shared/EmuSettings.h"
#include "Shared/Interfaces/IConsole.h"
#include "Utilities/FolderUtilities.h"
#include "Utilities/VirtualFile.h"
#include <fstream>
#include <execinfo.h>
#include <signal.h>
#include <unistd.h>
int main(int argc,char**argv){
 signal(SIGSEGV,[](int){void* a[40];int n=backtrace(a,40);backtrace_symbols_fd(a,n,2);_exit(139);});
 if(argc<3)return 2;
 FolderUtilities::SetHomeFolder("/tmp/atwc_mesen_home");
 Emulator emu;emu.Initialize(false);emu.GetSettings()->SetFlag(EmulationFlags::TestMode);emu.GetSettings()->SetFlag(EmulationFlags::MaximumSpeed);
 if(!emu.LoadRom(VirtualFile(argv[1]),VirtualFile(),true)){std::cerr<<"load failed\n";return 3;}
 auto c=emu.GetConsole();
 while(emu.GetFrameCount()<unsigned(atoi(argv[2])))std::this_thread::sleep_for(std::chrono::milliseconds(1));
 emu.Pause();
 {auto lock=emu.AcquireLock();
 auto f=emu.GetPpuFrame();std::string prefix=argc>3?argv[3]:"/tmp/ebg";std::ofstream out(prefix+"_frame.bin",std::ios::binary);out.write((char*)f.FrameBuffer,f.FrameBufferSize);out.close();auto ram=emu.GetMemory(MemoryType::NesInternalRam);std::ofstream rout(prefix+"_ram.bin",std::ios::binary);rout.write((char*)ram.Memory,ram.Size);rout.close();
 std::cout<<"Ran "<<f.FrameCount<<" frames, "<<f.Width<<"x"<<f.Height<<std::endl;
 }
 emu.Stop(false);emu.Release();return 0;
}

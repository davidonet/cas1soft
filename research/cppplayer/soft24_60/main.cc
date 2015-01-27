#include <boost/filesystem/operations.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>

extern "C" { 
#include <libavcodec/avcodec.h> 
}
extern "C" { 
#include <libavformat/avformat.h> 
}
extern "C" { 
#include <libswscale/swscale.h> 
}
#include <iostream>
#include <SDL.h>

#include "vsManager.h"

using namespace std;
using namespace boost::posix_time;


int main(int argc, char *argv[])
{

  vector<string> aMinuteVideoCont(60);
  boost::filesystem::directory_iterator end_itr;
  
  av_register_all();
  if(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER))
    cerr << "Could not initialize SDL - " 
	 << SDL_GetError() << endl;
  
  
  vsManager aManager(1280,720);
  aManager.setup();
  aManager.run();
  SDL_Quit();
}
















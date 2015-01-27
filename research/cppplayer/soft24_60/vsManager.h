#ifndef VSMANAGER_H
#define VSMANAGER_H


extern "C" { 
#include <libavcodec/avcodec.h> 
}
extern "C" { 
#include <libavformat/avformat.h> 
}
extern "C" { 
#include <libswscale/swscale.h> 
}
#include <boost/filesystem/operations.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/random/uniform_int.hpp>
#include <boost/random/variate_generator.hpp>
#include <vector>
#include <string>
#include <iostream>
#include <SDL.h>
#include <SDL/SDL_image.h>
#include <SDL_Pango.h>

#include "vsVideoPlayer.h"

using namespace std;

class vsManager
{
  int theWidth;
  int theHeight;
  vsVideoPlayer * theAdultFrame;
  vsVideoPlayer * theChildFrame;
  
  SDL_Surface      *theScreen;
 
  SDLPango_Context *theClockContext;
  SDLPango_Context *theInfosContext;
    
  unsigned long theCurrentHour;
  unsigned long theCurrentMinute;
  bool          isKeepOn;
  
 public:
  vsManager(int aWidth, int aHeight);
  void setup();
  void run();
  string chooseMinuteVideo();
  string chooseHourVideo();
  void updateMinuteVideo();
  void updateHourVideo();
  void updateClock();
  void displayInfos(vsVideoPlayer * aPlayer, SDL_Rect aRect);
};

#endif

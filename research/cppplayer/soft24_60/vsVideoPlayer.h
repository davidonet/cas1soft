#ifndef VSVIDEOPLAYER_H
#define VSVIDEOPLAYER_H

#include <cc++/thread.h>

#include <vector>
#include <list>
#include <string>

extern "C" { 
#include <libavcodec/avcodec.h> 
}
extern "C" { 
#include <libavformat/avformat.h> 
}
extern "C" { 
#include <libswscale/swscale.h> 
}

#include <SDL.h>

class vsVideoPlayer : public ost::Thread
{
    AVFormatContext *theFormatCtx;
    AVCodecContext  *theCodecCtx;
    AVCodec         *theCodec;
    AVFrame         *theFrame;
    AVFrame         *theRGBFrame;
    AVPacket         thePacket;
    int              theVideoStreamIdx;
  
    SDL_Rect         theRect;

    SwsContext      *theImageConvertCtx;

    bool             isRunnable;
    ost::Mutex       isRunnableMutex;
    bool             isFrameWaiting;
    ost::Mutex       isFrameWaitingMutex;

    std::string theName;
    std::string theAge;
    std::string theYear;
    std::string thePlace;

  
 public:
    SDL_Surface     *theOverlay;
 
    vsVideoPlayer(int aX, int aY, int aWidth, int aHeight);
    ~vsVideoPlayer();
    void setup();
    bool load(std::string aFileName);
    void run();
    void stop();
    void displayFrame(SDL_Surface * aScreen);
    std::string getName();
    std::string getAge();
    std::string getYear();
    std::string getPlace();
};

#endif


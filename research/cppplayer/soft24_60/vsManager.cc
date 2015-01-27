#include "vsManager.h"
#include <iostream>


#include <boost/filesystem/operations.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>

using namespace std;
using namespace boost::posix_time;

vsManager::vsManager(int aWidth, int aHeight):
    theWidth( aWidth ),
    theHeight( aHeight ),
    theAdultFrame(0),
    theChildFrame(0),
    theCurrentHour(-1),
    theCurrentMinute(-1),
    isKeepOn(true)
{
}

void vsManager::setup()
{  
    if(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER))
	cerr << "Could not initialize SDL - " 
	     << SDL_GetError() << endl;

    if(SDLPango_Init())
	cerr << "Could not initialize Pango - " 
	     << SDL_GetError() << endl;
    
    av_register_all();

    theScreen = SDL_SetVideoMode(theWidth, theHeight, 0,SDL_HWSURFACE | SDL_FULLSCREEN);
    if( !theScreen )
	cerr << "SDL: could not set video mode - exiting" << endl;
    
    theClockContext = SDLPango_CreateContext_GivenFontDesc("Deja Vu Sans Bold 24");
    SDLPango_SetDpi(theClockContext, 100.0, 100.0);
    SDLPango_SetDefaultColor(theClockContext,MATRIX_BLACK_BACK);
    theInfosContext = SDLPango_CreateContext_GivenFontDesc("Deja Vu Sans 14");
    SDLPango_SetDpi(theInfosContext, 100.0, 100.0);
    SDLPango_SetDefaultColor(theInfosContext,MATRIX_BLACK_BACK);
}


void vsManager::run()
{
/* while (keepOn)
   if newhour
   load new hour video
   display hour info
   if newminute
   load new minute video
   display minute info
   update clock
   refresh video frame
*/     
    unsigned long aLastMinute = -1;
    unsigned long aLastHour   = -1;
    SDL_Event anEvent; 
    Uint32 aTick=SDL_GetTicks();
    while( isKeepOn )
    {
	ptime now( microsec_clock::local_time() );
	time_duration aNowHour = now.time_of_day();
	theCurrentHour = aNowHour.hours();
	theCurrentMinute = aNowHour.minutes();
	
	if(theAdultFrame)
	    theAdultFrame->displayFrame(theScreen);

	if(theChildFrame)
	    theChildFrame->displayFrame(theScreen);

	SDL_UpdateRect(theScreen,0,theHeight/6,theWidth,theHeight/1.6);

	if( theCurrentMinute != aLastMinute )
	{
	    updateMinuteVideo(); 
	    updateClock();
	    aLastMinute = theCurrentMinute;
	}
	
	if(theCurrentHour != aLastHour)
	{
	    updateHourVideo();
	    updateClock();
	    aLastHour = theCurrentHour;
	}
	
	while (SDL_PollEvent(&anEvent))
	    switch( anEvent.type) {
	    case SDL_KEYDOWN:
	    {
		switch(anEvent.key.keysym.sym)
		{
			case SDLK_ESCAPE:
				isKeepOn = false;
				break;
			default:
				break;
		}
	    }
	    case SDL_QUIT:
		isKeepOn = false;
		break;
	    default:
		break;
	    }

	while( (microsec_clock::local_time() - now).total_milliseconds() <= 38 )
	{
	    usleep( 5000 );
	}
	
    }
}

void vsManager::updateMinuteVideo()
{
    if(theChildFrame)
	delete theChildFrame;
    theChildFrame = new vsVideoPlayer(theWidth/2,theHeight/6,
				      theWidth/2,theHeight/1.6);
    theChildFrame->setup();
    theChildFrame->load(chooseMinuteVideo());
    theChildFrame->start();
    SDL_Rect aRect;
    aRect.x=theWidth/2+theWidth/100;
    aRect.y=theHeight/1.25;
    displayInfos(theChildFrame,aRect);
}

string vsManager::chooseMinuteVideo()
{
    long aMinuteCounter = 0;
    vector<string> aMinuteVideoCont(120);
    string aFolder("video_24_60/60/");
    boost::filesystem::directory_iterator end_itr;
    for( boost::filesystem::directory_iterator itr( aFolder );
	 itr != end_itr;
	 ++itr )
    {
	aMinuteVideoCont[aMinuteCounter]=itr->leaf();
	aMinuteCounter++;
    }
    cout << "Found " << aMinuteCounter 
	 << " One minute videos" << endl;

    return aFolder + aMinuteVideoCont[random()%aMinuteCounter];
}


void vsManager::updateHourVideo()
{
     if(theAdultFrame)
		delete theAdultFrame;
     theAdultFrame = new vsVideoPlayer(0,theHeight/6,theWidth/2,
				       theHeight/1.6);
     theAdultFrame->setup();
     theAdultFrame->load(chooseHourVideo());
     theAdultFrame->start();
     SDL_Rect aRect;
     aRect.x=theWidth/100;
     aRect.y=theHeight/1.25;
     displayInfos(theAdultFrame,aRect);
}

string vsManager::chooseHourVideo()
{
    string aFolder("video_24_60/");
    if( theCurrentHour < 10 )
	aFolder += "0";
    stringstream aFolderComplement;
    aFolderComplement << theCurrentHour;
    aFolder += aFolderComplement.str();
    aFolder += "/";
    cout << "Folder : " << aFolder << endl;
    vector<string> aHourVideoCont(10);
    int aHourCounter=0;
    boost::filesystem::directory_iterator end_itr;
    for( boost::filesystem::directory_iterator itr(aFolder);
	 itr != end_itr;
	 ++itr )
    {
	aHourVideoCont[aHourCounter] = itr->leaf();
	aHourCounter++;
    }
    cout << "Found " << aHourCounter 
	 << " videos for hour " << theCurrentHour << endl;
    return aFolder + aHourVideoCont[random()%aHourCounter];
    
}

void vsManager::updateClock()
{
    SDL_Surface      *aClockSurface;
    string aClockStr("<span color='#75745f'>");
    stringstream aHourStr; 
    if(theCurrentHour <10)
	aClockStr += "0";
    aHourStr << theCurrentHour;
    aClockStr += aHourStr.str();
    aClockStr += ":";
    if(theCurrentMinute <10)
	aClockStr += "0";
    stringstream aMinuteStr;
    aMinuteStr << theCurrentMinute;
    aClockStr += aMinuteStr.str();
    aClockStr += "</span>";
    SDLPango_SetMarkup(theClockContext,aClockStr.c_str(),-1);
    SDLPango_SetMinimumSize(theClockContext, theWidth/2, 0); 
    aClockSurface = SDLPango_CreateSurfaceDraw(theClockContext);
    SDL_Rect aRect;
    aRect.x=(theWidth / 2) - 53;
    aRect.y=theHeight/20;
    aRect.w=105;
    aRect.h=theHeight/7;
    SDL_BlitSurface( aClockSurface, NULL, theScreen, &aRect );
    SDL_UpdateRect(theScreen,aRect.x,aRect.y,aRect.w,aRect.h);
    SDL_FreeSurface( aClockSurface );
}

void vsManager::displayInfos(vsVideoPlayer * aPlayer, SDL_Rect aRect)
{
    SDL_Surface     * aDisplaySurface;
    string anInfo; 
    anInfo += "<big><b><span color='#8f8e5d'>";    
    anInfo += aPlayer->getName();
    anInfo += "</span></b></big> <span color='#8f8e74'>               \n";
    anInfo += aPlayer->getAge(); 
    anInfo += "</span><span color='#6e6c58'>                           \n<small>";
    anInfo += aPlayer->getPlace();
    anInfo += "                   \n<i>";
    anInfo += aPlayer->getYear();
    anInfo += "                             </i></small></span>";
    SDLPango_SetMarkup(theInfosContext,anInfo.c_str(),-1);
    SDLPango_SetMinimumSize(theInfosContext, theWidth/2, 0);
    aDisplaySurface = SDLPango_CreateSurfaceDraw(theInfosContext);
    SDL_BlitSurface( aDisplaySurface, NULL, theScreen, &aRect );
    SDL_UpdateRect(theScreen,aRect.x,aRect.y,aRect.w,aRect.h);
    SDL_FreeSurface( aDisplaySurface );
}

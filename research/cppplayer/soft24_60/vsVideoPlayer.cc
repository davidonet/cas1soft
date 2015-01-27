#include "vsVideoPlayer.h"

#include <iostream>

using namespace std;

vsVideoPlayer::vsVideoPlayer(int aX, int aY, int aWidth, int aHeight) :
	isFrameWaiting(false), isRunnable(false), theFormatCtx(NULL),
			theCodecCtx(NULL), theCodec(NULL), theFrame(NULL),
			theRGBFrame(NULL), theImageConvertCtx(NULL)
{
	theRect.x = aX;
	theRect.y = aY;
	theRect.w = aWidth;
	theRect.h = aHeight + 2;
}

vsVideoPlayer::~vsVideoPlayer()
{
	stop();
	while (isRunning())
		SDL_Delay(1);
	av_freep(theRGBFrame);
}

void vsVideoPlayer::setup()
{

	theFrame = avcodec_alloc_frame();
	theRGBFrame = avcodec_alloc_frame();
	uint8_t *buffer;
	int numBytes;
	// Determine required buffer size and allocate buffer
	numBytes = avpicture_get_size(PIX_FMT_RGB24, theRect.w, theRect.h);
	buffer = (uint8_t *) av_malloc(numBytes * sizeof(uint8_t));
	avpicture_fill((AVPicture *) theRGBFrame, buffer, PIX_FMT_RGB24, theRect.w,
			theRect.h);

	theOverlay = SDL_CreateRGBSurfaceFrom(buffer, theRect.w, theRect.h, 24,
			theRect.w * 3, 0x000000ff, 0x0000ff00, 0x00ff0000, 0x00000000);
	if (theOverlay == NULL)
	{
		cerr << "Cannot create RGB Surface" << endl;
	}
}

bool vsVideoPlayer::load(string aFileName)
{
	if (av_open_input_file(&theFormatCtx, aFileName.c_str(), NULL, 0, NULL)
			!= 0)
	{
		cerr << " Could not open file : " << aFileName << endl;
		return false;
	}

	AVMetadata *m = theFormatCtx->metadata;

	if (m != NULL)
	{
		AVMetadataTag *tag = NULL;

		av_log(NULL, AV_LOG_INFO, "%sMetadata:\n", "   ");
		while ((tag = av_metadata_get(m, "", tag, AV_METADATA_IGNORE_SUFFIX)))
		{
			if (strcmp("language", tag->key))
			{
				av_log(NULL, AV_LOG_INFO, "%s  %-16s: %s\n", "   ", tag->key,
						tag->value);
				if (!strcmp("INAM", tag->key))
					theName = tag->value;
				if (!strcmp("IART", tag->key))
					theAge = tag->value;
				if (!strcmp("ICOP", tag->key))
					theYear = tag->value;
				if (!strcmp("ICMT", tag->key))
					thePlace = tag->value;
			}
		}
	}

	if (av_find_stream_info(theFormatCtx) < 0)
	{
		cerr << "Could not find stream info on : " << aFileName << endl;
		return false;
	}

	theVideoStreamIdx = -1;
	for (int i = 0; i < theFormatCtx->nb_streams; i++)
		if (theFormatCtx->streams[i]->codec->codec_type == CODEC_TYPE_VIDEO)
		{
			theVideoStreamIdx = i;
			break;
		}

	if (theVideoStreamIdx == -1)
	{
		cerr << "Didn't find a video stream : " << aFileName << endl;
		return false;
	}

	theCodecCtx = theFormatCtx->streams[theVideoStreamIdx]->codec;
	theCodec = avcodec_find_decoder(theCodecCtx->codec_id);

	if (theCodec == NULL)
	{
		cerr << "Unsupported codec : " << aFileName << endl;
		return false;
	}

	if (avcodec_open(theCodecCtx, theCodec) < 0)
	{
		cerr << "Could not open teh codec : " << aFileName << endl;
		return false;
	}

	theImageConvertCtx = sws_getContext(theCodecCtx->width,
			theCodecCtx->height, theCodecCtx->pix_fmt, theRect.w, theRect.h,
			PIX_FMT_RGB24, SWS_BICUBIC, NULL, NULL, NULL);

	/*
	 theImageConvertCtx = sws_alloc_context();

	 if (theImageConvertCtx == NULL)
	 {
	 cerr << "Cannot initialize the conversion context : " << aFileName
	 << endl;
	 return false;
	 }
	 av_set_int(theImageConvertCtx, "srcw", theCodecCtx->width);
	 av_set_int(theImageConvertCtx, "srch", theCodecCtx->height);
	 av_set_int(theImageConvertCtx, "src_format", theCodecCtx->pix_fmt);
	 av_set_int(theImageConvertCtx, "dstw", theRect.w);
	 av_set_int(theImageConvertCtx, "dsth", theRect.h);
	 av_set_int(theImageConvertCtx, "dst_format", PIX_FMT_RGB24);
	 av_set_int(theImageConvertCtx, "sws_flags", SWS_BICUBIC);
	 if (sws_init_context(theImageConvertCtx, NULL, NULL) < 0)
	 {
	 cerr << "Cannot initialize the conversion context : " << aFileName
	 << endl;
	 sws_freeContext(theImageConvertCtx);
	 return false;
	 }
	 */
	isRunnable = true;
	return true;
}

void vsVideoPlayer::stop()
{
	isFrameWaitingMutex.enterMutex();
	isFrameWaiting = false;
	isFrameWaitingMutex.leaveMutex();
	isRunnableMutex.enter();
	isRunnable = false;
	isRunnableMutex.leave();
}

void vsVideoPlayer::run()
{
	int isFrameFinished;
	isRunnableMutex.enter();
	bool aRun = isRunnable;
	isRunnableMutex.leave();
	while (aRun && av_read_frame(theFormatCtx, &thePacket) >= 0)
	{
		if (thePacket.stream_index == theVideoStreamIdx)
		{
			avcodec_decode_video2(theCodecCtx, theFrame, &isFrameFinished,&thePacket);

			if (isFrameFinished)
			{
				isFrameWaitingMutex.enterMutex();
				bool aFrameIsWaiting = isFrameWaiting;
				isFrameWaitingMutex.leaveMutex();
				while (aFrameIsWaiting)
				{
					SDL_Delay(5);
					isFrameWaitingMutex.enterMutex();
					aFrameIsWaiting = isFrameWaiting;
					isFrameWaitingMutex.leaveMutex();
				}

				sws_scale(theImageConvertCtx, theFrame->data,
						theFrame->linesize, 0, theCodecCtx->height,
						theRGBFrame->data, theRGBFrame->linesize);

				isFrameWaitingMutex.enterMutex();
				isFrameWaiting = true;
				isFrameWaitingMutex.leaveMutex();

			}
		}
		av_free_packet(&thePacket);
		isRunnableMutex.enter();
		aRun = isRunnable;
		isRunnableMutex.leave();
	}
	av_free_packet(&thePacket);
	av_free(theFrame);
	av_close_input_file(theFormatCtx);
	avcodec_close(theCodecCtx);
	sws_freeContext(theImageConvertCtx);
	cout << "Decoder Stopped" << endl;
	cout.flush();
}

void vsVideoPlayer::displayFrame(SDL_Surface * aScreen)
{
	isFrameWaitingMutex.enterMutex();
	if (isFrameWaiting && isRunnable)
	{

		SDL_BlitSurface(theOverlay, NULL, aScreen, &theRect);
		isFrameWaiting = false;
	}
	isFrameWaitingMutex.leaveMutex();
}

string vsVideoPlayer::getName()
{
	return theName;
}

string vsVideoPlayer::getAge()
{
	return theAge;
}

string vsVideoPlayer::getYear()
{
	return theYear;
}

string vsVideoPlayer::getPlace()
{
	return thePlace;
}

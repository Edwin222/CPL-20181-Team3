#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <iostream>
#include "Windows.h"
#include <HCNetSDK.h>
#include <time.h>

#pragma comment(lib, "HCNetSDK.lib")

using namespace std;

typedef HWND(WINAPI *PROCGETCONSOLEWINDOW)();
PROCGETCONSOLEWINDOW GetConsoleWindowAPI;

void CALLBACK g_ExceptionCallBack(DWORD dwType, LONG lUserID, LONG lHandle, void *pUser)
{
	char tempbuf[256] = { 0 };
	switch (dwType)
	{
	case EXCEPTION_RECONNECT:    //Reconnect in live view
		printf("----------reconnect--------%d\n", time(NULL));
		break;
	default:
		break;
	}
}

void main() {

	//---------------------------------------
	// Initialize
	NET_DVR_Init();
	//Set connected time and reconnected time
	NET_DVR_SetConnectTime(2000, 1);
	NET_DVR_SetReconnect(10000, true);

	//---------------------------------------
	//Set callback function of exception message
	NET_DVR_SetExceptionCallBack_V30(0, NULL, g_ExceptionCallBack, NULL);

	//---------------------------------------
	// Get window handle of control center
	HMODULE hKernel32 = GetModuleHandle("kernel32");
	GetConsoleWindowAPI = (PROCGETCONSOLEWINDOW)GetProcAddress(hKernel32, "GetConsoleWindow");

	//---------------------------------------
	// Register device
	LONG lUserID;

	//Login parameters, including IP address, user name, and password, etc.
	NET_DVR_USER_LOGIN_INFO struLoginInfo = { 0 };
	struLoginInfo.bUseAsynLogin = 0; //synchronous login mode
	strcpy(struLoginInfo.sDeviceAddress, "10.13.35.229"); //IP Address
	struLoginInfo.wPort = 8000; //Service port
	strcpy(struLoginInfo.sUserName, "admin"); //User name
	strcpy(struLoginInfo.sPassword, "abcd1234"); //Password

												 //Device information, output parameters
	NET_DVR_DEVICEINFO_V40 struDeviceInfoV40 = { 0 };

	lUserID = NET_DVR_Login_V40(&struLoginInfo, &struDeviceInfoV40);
	if (lUserID < 0)
	{
		printf("Login failed, error code: %d\n", NET_DVR_GetLastError());
		NET_DVR_Cleanup();
		return;
	}

	//---------------------------------------
	//Start live view and set callback data stream
	LONG lRealPlayHandle;
	HWND hWnd = GetConsoleWindowAPI();     //Get window handle
	NET_DVR_PREVIEWINFO struPlayInfo = { 0 };
	struPlayInfo.hPlayWnd = hWnd;         //Set the handle as valid when the stream should be decoded by SDK, while set the handle as null when only streaming.
	struPlayInfo.lChannel = 1;       //Live view channel No.
	struPlayInfo.dwStreamType = 0; // 0 - Main Stream, 1 - Sub - Stream, 2 - Stream 3, 3 - Stream 4, and so on.
		struPlayInfo.dwLinkMode = 0;       //0-TCP Mode, 1-UDP Mode, 2-Multi-play mode, 3-RTP Mode, 4-RTP/RTSP, 5-RSTP/HTTP
	struPlayInfo.bBlocked = 1;       //0-Non-Blocking Streaming, 1-Blocking Streaming

	lRealPlayHandle = NET_DVR_RealPlay_V40(lUserID, &struPlayInfo, NULL, NULL);
	if (lRealPlayHandle < 0)
	{
		printf("NET_DVR_RealPlay_V40 error\n");
		NET_DVR_Logout(lUserID);
		NET_DVR_Cleanup();
		return;
	}

	Sleep(10000);
	//---------------------------------------
	//Stop live view
	NET_DVR_StopRealPlay(lRealPlayHandle);
	//User logout
	NET_DVR_Logout(lUserID);
	//Release SDK resource
	NET_DVR_Cleanup();

	return;
}


#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <iostream>
#include <fstream>
#include "Windows.h"
#include "HCNetSDK.h"
#include <time.h>

using namespace std;

//Macro Definition of Time Resolution
#define GET_YEAR(_time_)      (((_time_)>>26) + 2000) 
#define GET_MONTH(_time_)     (((_time_)>>22) & 15)
#define GET_DAY(_time_)       (((_time_)>>17) & 31)
#define GET_HOUR(_time_)      (((_time_)>>12) & 31) 
#define GET_MINUTE(_time_)    (((_time_)>>6)  & 63)
#define GET_SECOND(_time_)    (((_time_)>>0)  & 63)

int pictureCount = 0;
LONG lRealPlayHandle;

BOOL CALLBACK MessageCallback(LONG lCommand, NET_DVR_ALARMER *pAlarmer, char *pAlarmInfo, DWORD dwBufLen, void* pUser)
{
	switch (lCommand)
	{
	case COMM_ALARM_FACE_DETECTION:
	{
		NET_DVR_FACE_DETECTION struFaceDetectionAlarm = { 0 };
		memcpy(&struFaceDetectionAlarm, pAlarmInfo, sizeof(NET_DVR_FACE_DETECTION));

		printf("detection\n");
	}
	break;
	case COMM_UPLOAD_FACESNAP_RESULT: //Face detection alarm information
	{
		char cFileName[256] = { 0 };
		sprintf(cFileName, "FaceSnapPick_%d.jpg", pictureCount);
		NET_DVR_CapturePicture(lRealPlayHandle, cFileName);
		pictureCount++;

		printf("Shotted\n");
	}
	break;
	/*
	case COMM_UPLOAD_FACESNAP_RESULT: //Face capture alarm information
	{
		NET_VCA_FACESNAP_RESULT struFaceSnap = { 0 };
		memcpy(&struFaceSnap, pAlarmInfo, sizeof(NET_VCA_FACESNAP_RESULT));

		NET_DVR_TIME struAbsTime = { 0 };
		struAbsTime.dwYear = GET_YEAR(struFaceSnap.dwAbsTime);
		struAbsTime.dwMonth = GET_MONTH(struFaceSnap.dwAbsTime);
		struAbsTime.dwDay = GET_DAY(struFaceSnap.dwAbsTime);
		struAbsTime.dwHour = GET_HOUR(struFaceSnap.dwAbsTime);
		struAbsTime.dwMinute = GET_MINUTE(struFaceSnap.dwAbsTime);
		struAbsTime.dwSecond = GET_SECOND(struFaceSnap.dwAbsTime);

		//Save captured scene picture
		if (struFaceSnap.dwBackgroundPicLen > 0 && struFaceSnap.pBuffer2 != NULL)
		{
			printf("In If\n");
			char cFilename[256] = { 0 };
			HANDLE hFile;
			DWORD dwReturn;

			char chTime[128];
			sprintf(chTime, "%4.4d%2.2d%2.2d%2.2d%2.2d%2.2d", struAbsTime.dwYear, struAbsTime.dwMonth, struAbsTime.dwDay, struAbsTime.dwHour, struAbsTime.dwMinute, struAbsTime.dwSecond);

			sprintf(cFilename, "FaceSnapBackPic[%s][%s].jpg", struFaceSnap.struDevInfo.struDevIP.sIpV4, chTime);

			hFile = CreateFile(cFilename, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
			if (hFile == INVALID_HANDLE_VALUE)
			{
				break;
			}
			WriteFile(hFile, struFaceSnap.pBuffer2, struFaceSnap.dwBackgroundPicLen, &dwReturn, NULL);
			CloseHandle(hFile);
			hFile = INVALID_HANDLE_VALUE;
		}

		printf("Face capture alarm[0x%x]: Abs[%4.4d%2.2d%2.2d%2.2d%2.2d%2.2d] Dev[ip:%s,port:%d,ivmsChan:%d] \n", \
			lCommand, struAbsTime.dwYear, struAbsTime.dwMonth, struAbsTime.dwDay, struAbsTime.dwHour, \
			struAbsTime.dwMinute, struAbsTime.dwSecond, struFaceSnap.struDevInfo.struDevIP.sIpV4, \
			struFaceSnap.struDevInfo.wPort, struFaceSnap.struDevInfo.byIvmsChannel);

		char cFileName[256] = { 0 };
		sprintf(cFileName, "FaceSnapPick_%d.jpg", pictureCount);
		NET_DVR_CapturePicture(lRealPlayHandle, cFileName);
		pictureCount++;
	}
	break;*/
	default:
		printf("Other alarms, alarm information type: 0x%x\n", lCommand);
		break;
	}

	return TRUE;
}

void main() {
	//---------------------------------------
	// Initialize
	NET_DVR_Init();
	//Set connected and reconnected time
	NET_DVR_SetConnectTime(2000, 1);
	NET_DVR_SetReconnect(10000, true);

	//---------------------------------------
	// Register device
	LONG lUserID;
	
	//Login parameter, including device IP address, user name, password and so on.
	NET_DVR_USER_LOGIN_INFO struLoginInfo = { 0 };
	struLoginInfo.bUseAsynLogin = 0; //Synchronous login mode
	strcpy(struLoginInfo.sDeviceAddress, "192.168.0.64"); //Device IP address
	struLoginInfo.wPort = 8000; //Device service port
	strcpy(struLoginInfo.sUserName, "admin"); //User name
	strcpy(struLoginInfo.sPassword, "q1w2e3r4!"); //Password
												 //Device information, output parameter
	NET_DVR_DEVICEINFO_V40 struDeviceInfoV40 = { 0 };
	
	lUserID = NET_DVR_Login_V40(&struLoginInfo, &struDeviceInfoV40);
	if (lUserID < 0)
	{
		printf("Login failed, error code: %d\n", NET_DVR_GetLastError());
		NET_DVR_Cleanup();
		return;
	}

	//Set alarm callback function
	NET_DVR_SetDVRMessageCallBack_V31(MessageCallback, NULL);

	//Enable arming
	LONG lHandle;
	NET_DVR_SETUPALARM_PARAM  struAlarmParam = { 0 };
	struAlarmParam.dwSize = sizeof(struAlarmParam);
	struAlarmParam.byFaceAlarmDetection = 0; //Face capture alarm, upload alarm information in the type of COMM_UPLOAD_FACESNAP_RESULT
											 //There is no need to set other arming parameters, not support

	lHandle = NET_DVR_SetupAlarmChan_V41(lUserID, &struAlarmParam);
	if (lHandle < 0)
	{
		printf("NET_DVR_SetupAlarmChan_V41 error, %d\n", NET_DVR_GetLastError());
		NET_DVR_Logout(lUserID);
		NET_DVR_Cleanup();
		return;
	}

	//---------------------------------------
	//Start live view and set callback data stream
	
	HWND hWnd = GetConsoleWindow();     //Get window handle
	NET_DVR_PREVIEWINFO struPlayInfo = { 0 };
	struPlayInfo.hPlayWnd = hWnd;         //Set the handle as valid when the stream should be decoded by SDK, while set the handle as null when only streaming.
	struPlayInfo.lChannel = 1;       //Live view channel No.
	struPlayInfo.dwStreamType = 0; // 0 - Main Stream, 1 - Sub - Stream, 2 - Stream 3, 3 - Stream 4, and so on.
	struPlayInfo.dwLinkMode = 0;       //0-TCP Mode, 1-UDP Mode, 2-Multi-play mode, 3-RTP Mode, 4-RTP/RTSP, 5-RSTP/HTTP
	struPlayInfo.bBlocked = 0;       //0-Non-Blocking Streaming, 1-Blocking Streaming

	lRealPlayHandle = NET_DVR_RealPlay_V40(lUserID, &struPlayInfo, NULL, NULL);
	if (lRealPlayHandle < 0)
	{
		printf("NET_DVR_RealPlay_V40 error\n");
		NET_DVR_Logout(lUserID);
		NET_DVR_Cleanup();
		return;
	}

	Sleep(50000); //During waiting, device will upload alarm information, and the alarm information will be received and handled in the alarm callback function.

				  //Disarm uploading channel
	if (!NET_DVR_CloseAlarmChan_V30(lHandle))
	{
		printf("NET_DVR_CloseAlarmChan_V30 error, %d\n", NET_DVR_GetLastError());
		NET_DVR_Logout(lUserID);
		NET_DVR_Cleanup();
		return;
	}

	NET_DVR_StopRealPlay(lRealPlayHandle);

	//User logout
	NET_DVR_Logout(lUserID);
	//Release SDK resource
	NET_DVR_Cleanup();
	return;
}


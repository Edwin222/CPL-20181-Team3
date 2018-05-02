#include <stdio.h>
#include <iostream>
#include "Windows.h"
#include "string.h"
#include "HCNetSDK.h"

using namespace std;
void main()
{
    int i=0;
    BYTE byIPID,byIPIDHigh;
    int iDevInfoIndex, iGroupNO, iIPCh;
    DWORD dwReturned = 0;

    //---------------------------------------
    // Initialize
    NET_DVR_Init();
    //set connected time and reconnected time
    NET_DVR_SetConnectTime(2000, 1);
    NET_DVR_SetReconnect(10000, true);

    //---------------------------------------
    // Register device
    LONG lUserID;

    //Login parameters, including IP address, user name, password and so on.
    NET_DVR_USER_LOGIN_INFO struLoginInfo = {0};
    struLoginInfo.bUseAsynLogin = 0; //Synchronous login mode
    strcpy(struLoginInfo.sDeviceAddress, "192.0.0.64"); //IP address
    struLoginInfo.wPort = 8000; //Service port
    strcpy(struLoginInfo.sUserName, "admin"); //User name
    strcpy(struLoginInfo.sPassword, "abcd1234"); //Password
  
    //Device information, output parameter
    NET_DVR_DEVICEINFO_V40 struDeviceInfoV40 = {0};

    lUserID = NET_DVR_Login_V40(&struLoginInfo, &struDeviceInfoV40);
    if (lUserID < 0)
    {
        printf("Login failed, error code: %d\n", NET_DVR_GetLastError());
        NET_DVR_Cleanup();
        return;
    }
    
    printf("The max number of analog channels: %d\n",struDeviceInfoV40.struDeviceV30.byChanNum); //Analog channel number
    printf("The max number of IP channels: %d\n", struDeviceInfoV40.struDeviceV30.byIPChanNum + struDeviceInfoV40.struDeviceV30.byHighDChanNum * 256);//Digital channel number

    //Get digital channel parameters
    NET_DVR_IPPARACFG_V40 IPAccessCfgV40;
    memset(&IPAccessCfgV40, 0, sizeof(NET_DVR_IPPARACFG));
    iGroupNO=0;
    if (!NET_DVR_GetDVRConfig(lUserID, NET_DVR_GET_IPPARACFG_V40, iGroupNO, &IPAccessCfgV40, sizeof(NET_DVR_IPPARACFG_V40), &dwReturned))
    {
        printf("NET_DVR_GET_IPPARACFG_V40 error, %d\n", NET_DVR_GetLastError());
        NET_DVR_Logout(lUserID);
        NET_DVR_Cleanup();
        return;
    }
    else
    {
        for (i=0;i<IPAccessCfgV40.dwDChanNum;i++)
        {
            switch(IPAccessCfgV40.struStreamMode[i].byGetStreamType)
            {
            case 0: //Get stream from device
                if (IPAccessCfgV40.struStreamMode[i].uGetStream.struChanInfo.byEnable)
                {
                    byIPID=IPAccessCfgV40.struStreamMode[i].uGetStream.struChanInfo.byIPID;
                    byIPIDHigh=IPAccessCfgV40.struStreamMode[i].uGetStream.struChanInfo.byIPIDHigh;
                    iDevInfoIndex=byIPIDHigh*256 + byIPID-1-iGroupNO*64;
                    printf("IP channel no.%d is online, IP: %s\n", i+1, IPAccessCfgV40.struIPDevInfo[iDevInfoIndex].struIP.sIpV4);
                }
                break;
            case 1: //Get stream from stream media server
                if (IPAccessCfgV40.struStreamMode[i].uGetStream.struPUStream.struStreamMediaSvrCfg.byValid)
                {
                    printf("IP channel %d connected with the IP device by stream server.\n", i+1);
                    printf("IP of stream server: %s, IP of IP device: %s\n",IPAccessCfgV40.struStreamMode[i].uGetStream.\
                    struPUStream.struStreamMediaSvrCfg.struDevIP.sIpV4, IPAccessCfgV40.struStreamMode[i].uGetStream.\
                    struPUStream.struDevChanInfo.struIP.sIpV4);
                }
                break;
            default:
                break;
            }
        }
    }
    
    //Set digital channel 5;
    iIPCh=4;

    //Support custom protocol
    NET_DVR_CUSTOM_PROTOCAL struCustomPro;
    if (!NET_DVR_GetDVRConfig(lUserID, NET_DVR_GET_CUSTOM_PRO_CFG, 1, &struCustomPro, sizeof(NET_DVR_CUSTOM_PROTOCAL), &dwReturned))
    //Get custom protocol 1
    {
        printf("NET_DVR_GET_CUSTOM_PRO_CFG error, %d\n", NET_DVR_GetLastError());
		NET_DVR_Logout(lUserID);
		NET_DVR_Cleanup();
        return;
    }
    struCustomPro.dwEnabled=1;   //Enable main stream
    struCustomPro.dwEnableSubStream=1; //Enable sub-stream
    strcpy((char *)struCustomPro.sProtocalName,"Protocal_RTSP");  //Custom protocol name: Protocal_RTSP, up to 16 bytes are allowed.
    struCustomPro.byMainProType=1;    //Protocol type of main stream: 1- RTSP
    struCustomPro.byMainTransType=2;  //Transmission protocol of main stream: 0- Auto, 1- udp, 2- rtp over rtsp
    struCustomPro.wMainPort=554;     //Streaming port of main stream
    strcpy((char *)struCustomPro.sMainPath,"rtsp://192.168.1.65/h264/ch1/main/av_stream");//Streaming URL of main stream
    struCustomPro.bySubProType=1;    //Protocol type of sub-stream: 1- RTSP
    struCustomPro.bySubTransType=2;  //Transmission protocol of sub-stream: 0- Auto, 1- udp, 2- rtp over rtsp
    struCustomPro.wSubPort=554;     //Streaming port of sub-stream
    strcpy((char *)struCustomPro.sSubPath,"rtsp://192.168.1.65/h264/ch1/sub/av_stream");//Streaming URL of sub-stream

    if (!NET_DVR_SetDVRConfig(lUserID, NET_DVR_SET_CUSTOM_PRO_CFG, 1, &struCustomPro, sizeof(NET_DVR_CUSTOM_PROTOCAL)))
    //Set custom protocol 1
    {
        printf("NET_DVR_SET_CUSTOM_PRO_CFG error, %d\n", NET_DVR_GetLastError());
        NET_DVR_Logout(lUserID);
        NET_DVR_Cleanup();
        return;
    }
    
    printf("Set the custom protocol: %s\n", "Protocal_RTSP");
    NET_DVR_IPC_PROTO_LIST m_struProtoList;
    if (!NET_DVR_GetIPCProtoList(lUserID, &m_struProtoList)) //Get protocol supported by front-end device
    {
        printf("NET_DVR_GetIPCProtoList error, %d\n", NET_DVR_GetLastError());
        NET_DVR_Logout(lUserID);
        NET_DVR_Cleanup();
        return;
    }

    IPAccessCfgV40.struIPDevInfo[iIPCh].byEnable=1;     //Enable
    for (i = 0; i<m_struProtoList.dwProtoNum; i++)
    {
        if(strcmp((char *)struCustomPro.sProtocalName,(char *)m_struProtoList.struProto[i].byDescribe)==0)
        {
            IPAccessCfgV40.struIPDevInfo[iIPCh].byProType=m_struProtoList.struProto[i].dwType; //Select custom protocol
            break;
        }
    }
    
    //IPAccessCfgV40.struIPDevInfo[iIPCh].byProType=0;  //Manufacturer private protocol
    strcpy((char *)IPAccessCfgV40.struIPDevInfo[iIPCh].struIP.sIpV4,"192.168.1.65"); //IP address of network camera
    IPAccessCfgV40.struIPDevInfo[iIPCh].wDVRPort=8000;  //Service port of network camera
    strcpy((char *)IPAccessCfgV40.struIPDevInfo[iIPCh].sUserName,"admin");  //User name of network camera
    strcpy((char *)IPAccessCfgV40.struIPDevInfo[iIPCh].sPassword,"12345");  //Password of network camera

    IPAccessCfgV40.struStreamMode[iIPCh].byGetStreamType=0;
    IPAccessCfgV40.struStreamMode[iIPCh].uGetStream.struChanInfo.byChannel=1;
    IPAccessCfgV40.struStreamMode[iIPCh].uGetStream.struChanInfo.byIPID=(iIPCh+1)%256;
    IPAccessCfgV40.struStreamMode[iIPCh].uGetStream.struChanInfo.byIPIDHigh=(iIPCh+1)/256;
    
    //Set digital channel, including adding, editing and deleting digital channel
    if (!NET_DVR_SetDVRConfig(lUserID, NET_DVR_SET_IPPARACFG_V40, iGroupNO, &IPAccessCfgV40, sizeof(NET_DVR_IPPARACFG_V40)))
    {
        printf("NET_DVR_SET_IPPARACFG_V40 error, %d\n", NET_DVR_GetLastError());
        NET_DVR_Logout(lUserID);
        NET_DVR_Cleanup();
        return;
    }
    else
    {
        printf("Set IP channel no.%d, IP: %s\n", iIPCh+1, IPAccessCfgV40.struIPDevInfo[iIPCh].struIP.sIpV4);
    }
    
    //User logout
    NET_DVR_Logout(lUserID);

    //Release SDK resource
    NET_DVR_Cleanup();
    return;
}


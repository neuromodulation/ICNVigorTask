#pragma once

#include "stdafx.h"
#include "resource.h"
#include "AOTypes.h"

#include "AOSystemAPI.h"

/////////////////////////////////////////////////////////////////////////
// CSystemSDKExampleDlg dialog

class CSystemSDKExampleDlg : public CDialogEx
{
public:
	CSystemSDKExampleDlg(CWnd* pParent = NULL);
	~CSystemSDKExampleDlg();

	enum { IDD = IDD_SYSTEMSDKEXAMPLE_DIALOG };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnTimer(UINT_PTR  nIDEvent);
	afx_msg void OnBnClickedBtnStartStopConnect();
	afx_msg void OnBnClickedBtnSetSavePath();
	afx_msg void OnBnClickedBtnSetSaveFileName();
	afx_msg void OnBnClickedBtnStartSave();
	afx_msg void OnBnClickedBtnStopSave();
	afx_msg void OnBnClickedBtnSendText();
	afx_msg void OnBnClickedBtnStimStart();
	afx_msg void OnBnClickedBtnStimStop();
	afx_msg void OnBnClickedBtnStimSetup();
	afx_msg void OnBnClickedBtnAnalogStimStart();
	afx_msg void OnBnClickedBtnAnalogStimStop();
	afx_msg void OnBnClickedBtnAnalogStimSetup();
	afx_msg void OnBnClickedBtnDOSend();
	afx_msg void OnBnClickedBtnDOSendDigOut();
	afx_msg void OnBnClickedBtnDOClear();
	afx_msg void OnBnClickedBtnDOClearDigOut();
	afx_msg void OnBnClickedBtnDIOListen();
	afx_msg void OnBnClickedBtnChannelsInfo();
	DECLARE_MESSAGE_MAP()

private:
	HICON   m_hIcon;
	BOOL    m_bStartConnection;
	int     m_nConnectionStatus;

	CStatic m_staticConnectionStatus;
	CStatic m_staticSystemTS;
	CStatic m_staticDriveDepth;
	CStatic m_staticDriveMoveTS;
	CStatic m_staticDriveStopTS;
	CButton m_btnConnect;
	CEdit   m_editSysMAC;
	CEdit   m_editHostMAC;
	CEdit   m_editSavePath;
	CEdit   m_editSaveFileName;
	CEdit   m_editText;
	int     m_nStimContactID;
	int     m_nStimReturnContactID;
	int     m_nAnalogStimContactID;
	int     m_nAnalogStimWaveID;
	int     m_nAnalogStimWaveFreq_Hz;
	float   m_fAnalogStimWaveDuration_Sec;
	int     m_nDOChannelID;
	int     m_nDOMask;
	int     m_nDOValue;
	int     m_nDIOChannelID;

	void UpdateConnectionStatus();
	void UpdateSystemTimestamp();
	void UpdateDriveStatus();
	void OnConnected();
	void OnDisconnected();

	MAC_ADDR GetSysMAC();
	MAC_ADDR GetHostMAC();

	CString GetSystemSDKError();
	void ShowSystemSDKError();
};

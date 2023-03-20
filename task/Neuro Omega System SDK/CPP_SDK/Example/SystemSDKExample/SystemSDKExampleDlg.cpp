#include "stdafx.h"
#include "SystemSDKExample.h"
#include "SystemSDKExampleDlg.h"
#include "DlgChannels.h"
#include "DlgDigitalStimSetup.h"
#include "DlgWaveForm.h"
#include "DlgCloseLoopTest.h"
#include "afxdialogex.h"
#include "AOddx.h"

#include <string>

/////////////////////////////////////////////////////////////////////////
// SystemSDK header files

#include "AOSystemAPI.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

/////////////////////////////////////////////////////////////////////////
// Globals

CString g_sDefaultSysMAC("F4:5E:AB:69:10:9E");
CString g_sDefaultHostMAC("00:15:17:63:8F:7F");

/////////////////////////////////////////////////////////////////////////

void DisplayError(cChar* pMessage, int nMessage); // Callback function to get back error messages.

/////////////////////////////////////////////////////////////////////////
// CSystemSDKExampleDlg dialog

CSystemSDKExampleDlg::CSystemSDKExampleDlg(CWnd* pParent /*=NULL*/)
	: CDialogEx(CSystemSDKExampleDlg::IDD, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
	m_bStartConnection            =  TRUE;
	m_nConnectionStatus           =  0;
	m_nStimContactID              =  0;
	m_nStimReturnContactID        = -1; // Global Return
	m_nAnalogStimContactID        =  0;
	m_nAnalogStimWaveID           =  0;
	m_nAnalogStimWaveFreq_Hz      =  1;
	m_fAnalogStimWaveDuration_Sec = 40;
	m_nDOChannelID                =  0;
	m_nDOMask                     =  0;
	m_nDOValue                    =  0;
	m_nDIOChannelID               =  0;

	SetCallBackDisplayError(DisplayError);
}

CSystemSDKExampleDlg::~CSystemSDKExampleDlg()
{
	SetCallBackDisplayError(NULL);
	AO_Exit();
}

void CSystemSDKExampleDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);

	DDX_Control(pDX, IDC_STATIC_CONNECTION_STAT, m_staticConnectionStatus);
	DDX_Control(pDX, IDC_STATIC_SYS_TS, m_staticSystemTS);
	DDX_Control(pDX, IDC_BTN_START_STOP_CONNECT, m_btnConnect);
	DDX_Control(pDX, IDC_EDIT_SYS_MAC, m_editSysMAC);
	DDX_Control(pDX, IDC_EDIT_HOST_MAC, m_editHostMAC);
	DDX_Control(pDX, IDC_EDIT_SAVE_PATH, m_editSavePath);
	DDX_Control(pDX, IDC_EDIT_SAVE_FILENAME, m_editSaveFileName);
	DDX_Control(pDX, IDC_EDIT_TEXT, m_editText);
	DDX_Control(pDX, IDC_STATIC_DRIVE_DEPTH, m_staticDriveDepth);
	DDX_Control(pDX, IDC_STATIC_DRIVE_MOVE_TS, m_staticDriveMoveTS);
	DDX_Control(pDX, IDC_STATIC_DRIVE_STOP_TS, m_staticDriveStopTS);

	AO_DDX_Int(pDX, IDC_EDIT_STIM_CONTACT_ID, "Stim. Contact ID", m_nStimContactID);
	AO_DDX_Int(pDX, IDC_EDIT_STIM_RETURN_ID, "Return Contact ID", m_nStimReturnContactID);
	AO_DDX_Int(pDX, IDC_EDIT_ANALOG_STIM_CONTACT, "Stim. Contact ID", m_nAnalogStimContactID);
	AO_DDX_Int(pDX, IDC_EDIT_ANALOG_STIM_WAVE_ID, "Wave ID", m_nAnalogStimWaveID);
	AO_DDX_Int(pDX, IDC_EDIT_ANALOG_STIM_WAVE_FREQ, "Frquency (Hz)", m_nAnalogStimWaveFreq_Hz);
	AO_DDX_Float(pDX, IDC_EDIT_ANALOG_STIM_WAVE_DURATION, "Duration (Sec)", m_fAnalogStimWaveDuration_Sec);
	AO_DDX_Int(pDX, IDC_EDIT_DO_CHANNEL_ID, "DO Channel ID", m_nDOChannelID);
	AO_DDX_Int(pDX, IDC_EDIT_DO_MASK, "DO Mask", m_nDOMask);
	AO_DDX_Int(pDX, IDC_EDIT_DO_VALUE, "DO Value", m_nDOValue);
	AO_DDX_Int(pDX, IDC_EDIT_DIO_CHANNEL_ID, "DIO Channel ID", m_nDIOChannelID);
}

BEGIN_MESSAGE_MAP(CSystemSDKExampleDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_TIMER()
	ON_BN_CLICKED(IDC_BTN_START_STOP_CONNECT, &CSystemSDKExampleDlg::OnBnClickedBtnStartStopConnect)
	ON_BN_CLICKED(IDC_BUTTON_SET_SAVE_PATH, &CSystemSDKExampleDlg::OnBnClickedBtnSetSavePath)
	ON_BN_CLICKED(IDC_BUTTON_SET_SAVE_FILENAME, &CSystemSDKExampleDlg::OnBnClickedBtnSetSaveFileName)
	ON_BN_CLICKED(IDC_BUTTON_SAVE_START, &CSystemSDKExampleDlg::OnBnClickedBtnStartSave)
	ON_BN_CLICKED(IDC_BUTTON_SAVE_STOP, &CSystemSDKExampleDlg::OnBnClickedBtnStopSave)
	ON_BN_CLICKED(IDC_BUTTON_SEND_TEXT, &CSystemSDKExampleDlg::OnBnClickedBtnSendText)
	ON_BN_CLICKED(IDC_BUTTON_STIM_START, &CSystemSDKExampleDlg::OnBnClickedBtnStimStart)
	ON_BN_CLICKED(IDC_BUTTON_STIM_STOP, &CSystemSDKExampleDlg::OnBnClickedBtnStimStop)
	ON_BN_CLICKED(IDC_BUTTON_STIM_SETUP, &CSystemSDKExampleDlg::OnBnClickedBtnStimSetup)
	ON_BN_CLICKED(IDC_BUTTON_ANALOG_STIM_START, &CSystemSDKExampleDlg::OnBnClickedBtnAnalogStimStart)
	ON_BN_CLICKED(IDC_BUTTON_ANALOG_STIM_STOP, &CSystemSDKExampleDlg::OnBnClickedBtnAnalogStimStop)
	ON_BN_CLICKED(IDC_BUTTON_ANALOG_STIM_SETUP, &CSystemSDKExampleDlg::OnBnClickedBtnAnalogStimSetup)
	ON_BN_CLICKED(IDC_BUTTON_DO_SEND, &CSystemSDKExampleDlg::OnBnClickedBtnDOSend)
	ON_BN_CLICKED(IDC_BUTTON_DO_SEND_DIGOUT, &CSystemSDKExampleDlg::OnBnClickedBtnDOSendDigOut)
	ON_BN_CLICKED(IDC_BUTTON_DO_CLEAR, &CSystemSDKExampleDlg::OnBnClickedBtnDOClear)
	ON_BN_CLICKED(IDC_BUTTON_DO_CLEAR_DIGOUT, &CSystemSDKExampleDlg::OnBnClickedBtnDOClearDigOut)
	ON_BN_CLICKED(IDC_BUTTON_DIO_LISTEN, &CSystemSDKExampleDlg::OnBnClickedBtnDIOListen)
	ON_BN_CLICKED(IDC_BUTTON_CHANNELS_INFO, &CSystemSDKExampleDlg::OnBnClickedBtnChannelsInfo)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////
// CSystemSDKExampleDlg message handlers

BOOL CSystemSDKExampleDlg::OnInitDialog()
{
	BOOL bRes = CDialogEx::OnInitDialog();

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon

	m_editSysMAC.SetWindowText(g_sDefaultSysMAC);
	m_editHostMAC.SetWindowText(g_sDefaultHostMAC);

	CMenu *pMenu = GetSystemMenu(FALSE);
	if (pMenu != NULL)
	{
		pMenu->InsertMenu(0, MF_BYPOSITION|MF_ENABLED, IDC_MENU_CLOSE_LOOP_TEST, "Close Loop Test");
		pMenu->InsertMenu(1, MF_BYPOSITION|MF_SEPARATOR);
	}

	SetTimer(1, 100, NULL);  // Connection Status
	SetTimer(2, 1000, NULL); // System Timestamp
	SetTimer(3, 200, NULL);  // Drive Status

	return bRes;  // return TRUE  unless you set the focus to a control
}

void CSystemSDKExampleDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	switch (nID)
	{
	case IDC_MENU_CLOSE_LOOP_TEST:
	{
		CDlgCloseLoopTest dlg;
		dlg.DoModal();
		break;
	}
	default:
	{
		CDialogEx::OnSysCommand(nID, lParam);
		break;
	}
	}
}

void CSystemSDKExampleDlg::OnTimer(UINT_PTR  nIDEvent)
{
	if (nIDEvent == 1)
		UpdateConnectionStatus();

	if (nIDEvent == 2)
		UpdateSystemTimestamp();

	if (nIDEvent == 3)
		UpdateDriveStatus();
}

void CSystemSDKExampleDlg::UpdateConnectionStatus()
{
	int nConnected = isConnected();

	if (nConnected == 0)
		m_staticConnectionStatus.SetWindowText("Disconnected");

	if (nConnected == 1)
		m_staticConnectionStatus.SetWindowText("Connected");

	if (nConnected == 2)
		m_staticConnectionStatus.SetWindowText("Connecting");

	if (m_nConnectionStatus != 1 && nConnected == 1)
		OnConnected(); // Just connected

	if (m_nConnectionStatus == 1 && nConnected != 1)
		OnDisconnected(); // Just disconnected

	m_nConnectionStatus = nConnected;
}

void CSystemSDKExampleDlg::UpdateSystemTimestamp()
{
	ULONG uSystemTS = 0;
	
	CString sSysTS = __T("");
	if (eAO_OK == GetLatestTimeStamp(&uSystemTS))
		sSysTS.Format("System Timestamp: %u", uSystemTS);
	else
		sSysTS.Format("System Timestamp: NA");
	m_staticSystemTS.SetWindowText(sSysTS);
}

void CSystemSDKExampleDlg::UpdateDriveStatus()
{
	EAOResult eAORes = eAO_OK;

	// Depth
	int32 nDepth = 0;
	eAORes = (EAOResult)GetDriveDepth(&nDepth);
	if (eAORes == eAO_OK)
	{
		CString sDepth = __T("");
		sDepth.Format("Depth: %02.3f", nDepth/1000.0);
		m_staticDriveDepth.SetWindowText(sDepth);
	}
	else
	{
		CString sError = GetSystemSDKError();
		m_staticDriveDepth.SetWindowText("Depth: NA");
	}

	// Move TS
	uint32 uMotorMoveTS = 0;
	eAORes = (EAOResult)GetMoveMotorTS(&uMotorMoveTS);
	if (eAORes == eAO_OK)
	{
		CString sMotorMoveTS = __T("");
		sMotorMoveTS.Format("Move TS: %u", uMotorMoveTS);
		m_staticDriveMoveTS.SetWindowText(sMotorMoveTS);
	}
	else
	{
		CString sError = GetSystemSDKError();
		m_staticDriveMoveTS.SetWindowText("Move TS: NA");
	}

	// Stop TS
	uint32 uMotorStopTS = 0;
	eAORes = (EAOResult)GetStopMotorTS(&uMotorStopTS);
	if (eAORes == eAO_OK)
	{
		CString sMotorStopTS = __T("");
		sMotorStopTS.Format("Stop TS: %u", uMotorStopTS);
		m_staticDriveStopTS.SetWindowText(sMotorStopTS);
	}
	else
	{
		CString sError = GetSystemSDKError();
		m_staticDriveStopTS.SetWindowText("Stop TS: NA");
	}
}

void CSystemSDKExampleDlg::OnConnected()
{
}

void CSystemSDKExampleDlg::OnDisconnected()
{
}

void CSystemSDKExampleDlg::OnBnClickedBtnStartStopConnect()
{
	// TODO: Add your control notification handler code here
	if (m_bStartConnection)
	{
		MAC_ADDR sysMAC  = GetSysMAC();
		MAC_ADDR hostMAC = GetHostMAC();
		int nRes = StartConnection(&sysMAC, &hostMAC, -1, NULL);
		if (nRes == eAO_OK)
		{
			m_bStartConnection = FALSE;
			m_btnConnect.SetWindowText("Disconnect");
		}
		else
		{
			CString sMsg = __T("");
			sMsg.Format("StartConnection failed: [%s]", GetSystemSDKError().GetBuffer());
			MessageBox(sMsg, "System SDK Example", MB_ICONERROR|MB_OK);
		}
	}
	else
	{
		CloseConnection();
		m_bStartConnection = TRUE;
		m_btnConnect.SetWindowText("Connect");
	}
}

void CSystemSDKExampleDlg::OnBnClickedBtnSetSavePath()
{
	CString sSavePath = __T("");

	m_editSavePath.GetWindowText(sSavePath);

	if (SetSavePath(sSavePath.GetBuffer(), sSavePath.GetLength()) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnSetSaveFileName()
{
	CString sSaveFileName = __T("");

	m_editSaveFileName.GetWindowText(sSaveFileName);

	if (SetSaveFileName(sSaveFileName.GetBuffer(), sSaveFileName.GetLength()) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnStartSave()
{
	if (StartSave() != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnStopSave()
{
	if (StopSave() != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnSendText()
{
	CString sText = __T("");

	m_editText.GetWindowText(sText);

	if (SendText(sText.GetBuffer(), sText.GetLength()) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnStimStart()
{
	if (!UpdateData(TRUE))
		return;

	if (StartStimulation(m_nStimContactID) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnStimStop()
{
	if (!UpdateData(TRUE))
		return;

	if (StopStimulation(m_nStimContactID) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnStimSetup()
{
	CDlgDigitalStimSetup m_dlgStimSetup;
	m_dlgStimSetup.DoModal();
}

void CSystemSDKExampleDlg::OnBnClickedBtnAnalogStimStart()
{
	if (!UpdateData(TRUE))
		return;

	if (eAO_OK != StartAnalogStimulation(m_nAnalogStimContactID,
										m_nAnalogStimWaveID,
										m_nAnalogStimWaveFreq_Hz,
										m_fAnalogStimWaveDuration_Sec,
										m_nStimReturnContactID))
	{
		ShowSystemSDKError();
	}
}

void CSystemSDKExampleDlg::OnBnClickedBtnAnalogStimStop()
{
	if (!UpdateData(TRUE))
		return;

	if (StopStimulation(m_nAnalogStimContactID) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnAnalogStimSetup()
{
	CDlgWaveForm m_dlgWaveForm;
	m_dlgWaveForm.DoModal();
}

void CSystemSDKExampleDlg::OnBnClickedBtnDOSend()
{
	if (!UpdateData(TRUE))
		return;

	if (SendDigitalData(m_nDOChannelID, m_nDOMask, m_nDOValue) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnDOSendDigOut()
{
	if (!UpdateData(TRUE))
		return;

	if (SendDout(m_nDOMask, m_nDOValue) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnDOClear()
{
	if (!UpdateData(TRUE))
		return;

	if (SendDigitalData(m_nDOChannelID, 0xFF, 0) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnDOClearDigOut()
{
	if (SendDout(0xFF, 0) != eAO_OK)
		ShowSystemSDKError();
}

void CSystemSDKExampleDlg::OnBnClickedBtnDIOListen()
{
	if (!UpdateData(TRUE))
		return;

	MessageBox("ListenToDigitalChannel will stuck the application for 5000 mSec untill the DIO channel received.");

	if (ListenToDigitalChannel(m_nDIOChannelID, 0x01, 5000) != eAO_OK)
		ShowSystemSDKError();
	else
		MessageBox("ListenToDigitalChannel: DIO channel received.");
}

void CSystemSDKExampleDlg::OnBnClickedBtnChannelsInfo()
{
	CDlgChannels dlgChannels;
	dlgChannels.DoModal();
}

MAC_ADDR CSystemSDKExampleDlg::GetSysMAC()
{
	CString sSysMAC;
	m_editSysMAC.GetWindowText(sSysMAC);

	MAC_ADDR sysMAC = {0};
	sscanf(sSysMAC.GetBuffer(), "%x:%x:%x:%x:%x:%x",
		&sysMAC.addr[0], &sysMAC.addr[1], &sysMAC.addr[2], &sysMAC.addr[3], &sysMAC.addr[4], &sysMAC.addr[5]);
	return sysMAC;
}

MAC_ADDR CSystemSDKExampleDlg::GetHostMAC()
{
	CString sHostMAC;
	m_editHostMAC.GetWindowText(sHostMAC);

	MAC_ADDR hostMAC = {0};
	sscanf(sHostMAC.GetBuffer(), "%x:%x:%x:%x:%x:%x",
		&hostMAC.addr[0], &hostMAC.addr[1], &hostMAC.addr[2], &hostMAC.addr[3], &hostMAC.addr[4], &hostMAC.addr[5]);
	return hostMAC;
}

CString CSystemSDKExampleDlg::GetSystemSDKError()
{
	char sError[1000] = {0};
	int  nErrorCount  = 0;

	ErrorHandlingfunc(&nErrorCount, sError, 1000);

	return CString(sError);
}

void CSystemSDKExampleDlg::ShowSystemSDKError()
{
	CString sError = GetSystemSDKError();
	AfxMessageBox(sError, MB_OK);
}

void DisplayError(cChar* pMessage, int nMessage)
{
	AfxMessageBox(pMessage, MB_OK);
}

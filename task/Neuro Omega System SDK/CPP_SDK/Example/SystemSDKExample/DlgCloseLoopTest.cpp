// DlgCloseLoopTest.cpp : implementation file
//

#include "stdafx.h"
#include "SystemSDKExample.h"
#include "DlgCloseLoopTest.h"
#include "afxdialogex.h"
#include "AOSystemAPI.h"
#include "AOddx.h"
#include "StreamFormat.h"
#include "AOMFCDebug.h"

using NS_AO_MFC::CAODebug;

///////////////////////////////////////////////////////////////////////////
// CDlgCloseLoopTest dialog

IMPLEMENT_DYNAMIC(CDlgCloseLoopTest, CDialogEx)

CDlgCloseLoopTest::CDlgCloseLoopTest(CWnd* pParent /*=NULL*/)
	: CDialogEx(CDlgCloseLoopTest::IDD, pParent)
{
	m_nDOChannelID   = 11701; // DIG-OUT
	m_nDOMask        = 0xFF;
	m_nDIChannelID   = 11348; // TTL 001
	m_nDIMask        = 0x01;
	m_nStimContactID = 10005; // Macro 01
	m_nTestLoops     = 100;
	m_bTestRunning   = false;
	m_bStopTest      = false;

	CAODebug::InitDebugFolder(CString("C:\\ClosedLoop\\"));
	CAODebug::DebugEnable(true);
}

CDlgCloseLoopTest::~CDlgCloseLoopTest()
{
}

void CDlgCloseLoopTest::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);

	DDX_Control(pDX, IDC_BUTTON_RUN_TEST, m_btnTest);

	AO_DDX_Int(pDX, IDC_EDIT_DO_CHANNEL, "Digital Output Channel", m_nDOChannelID);
	AO_DDX_Int(pDX, IDC_EDIT_DO_MASK, "Digital Output Mask", m_nDOMask);
	AO_DDX_Int(pDX, IDC_EDIT_DI_CHANNEL, "Digital Input Channel", m_nDIChannelID);
	AO_DDX_Int(pDX, IDC_EDIT_DI_MASK, "Digital Input Mask", m_nDIMask);
	AO_DDX_Int(pDX, IDC_EDIT_STIM_CONTACT, "Stimulation Contact", m_nStimContactID);
	AO_DDX_MinInt(pDX, IDC_EDIT_TEST_LOOPS, "Test Loops", 1, m_nTestLoops);
}

BEGIN_MESSAGE_MAP(CDlgCloseLoopTest, CDialogEx)
	ON_BN_CLICKED(IDC_BUTTON_RUN_TEST, &CDlgCloseLoopTest::OnBnClickedRunTest)
END_MESSAGE_MAP()

///////////////////////////////////////////////////////////////////////////
// CDlgCloseLoopTest message handlers

BOOL CDlgCloseLoopTest::OnInitDialog()
{
	BOOL bRes = CDialogEx::OnInitDialog();
	return bRes;
}

void CDlgCloseLoopTest::OnBnClickedRunTest()
{
	if (!m_bTestRunning)
	{
		m_bTestRunning = true;
		m_bStopTest    = false;
		m_btnTest.SetWindowText("Stop Test");

		CloseLoopTest();

		m_bTestRunning = false;
		m_btnTest.SetWindowText("Run Test");
		SetWindowText("Close Loop Test");
	}
	else
	{
		m_bStopTest = true;
	}
}

void CDlgCloseLoopTest::CloseLoopTest()
{
	if (!UpdateData(TRUE))
		return;

	// 1. Set the given channel stimulation parameters
	if (eAO_OK != SetStimulationParameters(0.1, 0.5, -0.1, 0.5, 1, 60, -1, m_nStimContactID))
	{
		ShowSystemSDKError();
		return;
	}

	// 2. Start acquisition on DI port
	if (eAO_OK != AddBufferChannel(m_nDIChannelID, 5000))
	{
		ShowSystemSDKError();
		return;
	}

	// 3. Start acquisition on Stim Marker 1
	if (eAO_OK != AddBufferChannel(11221, 5000))
	{
		ShowSystemSDKError();
		return;
	}

	CAODebug debugCloseLoopTest;
	debugCloseLoopTest.SetDebugFileName(CString("CloseLoobTest.txt"));

	debugCloseLoopTest.Trace(__LINE__, __FILE__, "Test Start");

	int16  *pData       = new int16[sizeofInWords(StreamDataBlock)];
	int     nData       = 0;
	uint32  uDI_TS      = 0;
	uint32  uSM_TS      = 0;
	CString sText       = __T("");
	double  fMinTime_mS = 100;
	double  fMaxTime_mS =   0;
	double  fAvgTime_mS =   0;
	int     nTestLoop   =   1;
	do 
	{
		sText.Format("Close Loop Test (%d)", nTestLoop);
		SetWindowText(sText);

		// Clear Digital Out Port
		if (eAO_OK != SendDigitalData(m_nDOChannelID, 0xFF, 0))
		{
			ShowSystemSDKError();
			break;
		}
		Sleep(500);

		// Clear Digital Input Port data
		while (eAO_OK == GetChannelData(m_nDIChannelID, pData, sizeofInWords(StreamDataBlock), &nData) && nData != 0){}

		// Clear StimMarker 1 data
		while (eAO_OK == GetChannelData(11221, pData, sizeofInWords(StreamDataBlock), &nData) && nData != 0){}

		// Send Digital Ouput
		if (eAO_OK != SendDigitalData(m_nDOChannelID, 0xFF, 0xFF))
		{
			ShowSystemSDKError();
			break;
		}

		// Wait for Digital Input
		while (eAO_OK != GetChannelData(m_nDIChannelID, pData, sizeofInWords(StreamDataBlock), &nData) || nData == 0){}

		uDI_TS = ((StreamDataBlock*)pData)->uTimeStamp;

		// Start Stimulation
		if (eAO_OK != StartStimulation(m_nStimContactID))
		{
			ShowSystemSDKError();
			break;
		}

		// Wait for StimMarker 1
		while (eAO_OK != GetChannelData(11221, pData, sizeofInWords(StreamDataBlock), &nData) || nData == 0){}

		uSM_TS = ((StreamDataBlock*)pData)->uTimeStamp;

		// Stop Stimulation
		if (eAO_OK != StopStimulation(m_nStimContactID))
		{
			ShowSystemSDKError();
			break;
		}
		
		double fTime = (uSM_TS - uDI_TS)/44.0;

		debugCloseLoopTest.Trace(__LINE__, __FILE__, "DI TS [%u] SM TS [%u] Time [%.03f] mSec",
			uDI_TS, uSM_TS, fTime);

		if (fMinTime_mS > fTime)
			fMinTime_mS = fTime;

		if (fMaxTime_mS < fTime)
			fMaxTime_mS = fTime;

		fAvgTime_mS = (fAvgTime_mS*(nTestLoop-1) + fTime)/nTestLoop;

		// The below code is for prevent the UI to stuck
		MSG msg;
		while (PeekMessage(&msg, m_hWnd,  0, 0, PM_REMOVE))
		{ 
			TranslateMessage(&msg);
			DispatchMessage(&msg);
		}
	} while (++nTestLoop <= m_nTestLoops && !m_bStopTest);

	delete[] pData;

	CString sTestSummary = __T("");
	sTestSummary.Format("Min Time [%.03f] mSec, Max Time [%0.03f] mSec, Avg Time [%0.03f] mSec",
					fMinTime_mS, fMaxTime_mS, fAvgTime_mS);

	debugCloseLoopTest.Trace(__LINE__, __FILE__, sTestSummary);

	MessageBox(sTestSummary);
}

CString CDlgCloseLoopTest::GetSystemSDKError()
{
	char sError[1000] = {0};
	int  nErrorCount  = 0;

	ErrorHandlingfunc(&nErrorCount, sError, 1000);

	return CString(sError);
}

void CDlgCloseLoopTest::ShowSystemSDKError()
{
	CString sError = GetSystemSDKError();
	AfxMessageBox(sError, MB_OK);
}

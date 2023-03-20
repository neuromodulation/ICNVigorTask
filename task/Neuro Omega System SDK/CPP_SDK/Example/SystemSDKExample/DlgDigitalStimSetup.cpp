// DlgDigitalStimSetup.cpp : implementation file
//

#include "stdafx.h"
#include "SystemSDKExample.h"
#include "DlgDigitalStimSetup.h"
#include "afxdialogex.h"
#include "AOddx.h"
#include "AOSystemAPI.h"


///////////////////////////////////////////////////////////////////////////
// CDlgDigitalStimSetup dialog

IMPLEMENT_DYNAMIC(CDlgDigitalStimSetup, CDialogEx)

CDlgDigitalStimSetup::CDlgDigitalStimSetup(CWnd* pParent /*=NULL*/)
	: CDialogEx(CDlgDigitalStimSetup::IDD, pParent)
{
	m_bError            =  false;
	m_nContactID        =  10000;
	m_nReturnChannel    =  -1; // Global Return
	m_fDuration_Sec     =  40.0;
	m_nFreq_Hz          =  130;
	m_fPhase1Delay_mSec =  0.0;
	m_fPhase2Delay_mSec =  0.0;
	m_fPhase1Width_mSec =  0.5;
	m_fPhase2Width_mSec =  0.5;
	m_fPhase1Amp_mAmp   =  0.1;
	m_fPhase2Amp_mAmp   = -0.1;
}

CDlgDigitalStimSetup::~CDlgDigitalStimSetup()
{
}

void CDlgDigitalStimSetup::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);

	AO_DDX_Int(pDX, IDC_EDIT_STIM_CONTACT_ID, "Stim. Contact", m_nContactID);
	AO_DDX_Int(pDX, IDC_EDIT_STIM_RETURN_ID, "Return Channel", m_nReturnChannel);
	AO_DDX_Float(pDX, IDC_EDIT_STIM_DURATION, "Duration (Sec)", m_fDuration_Sec);
	AO_DDX_Int(pDX, IDC_EDIT_STIM_FREQUENCY, "Frequency (Hz)", m_nFreq_Hz);
	AO_DDX_Float(pDX, IDC_EDIT_STIM_PHASE1_DELAY, "Phase 1 Delay (mSec)", m_fPhase1Delay_mSec);
	AO_DDX_Float(pDX, IDC_EDIT_STIM_PHASE2_DELAY, "Phase 2 Delay (mSec)", m_fPhase2Delay_mSec);
	AO_DDX_Float(pDX, IDC_EDIT_STIM_PHASE1_WIDTH, "Phase 1 Width (mSec)", m_fPhase1Width_mSec);
	AO_DDX_Float(pDX, IDC_EDIT_STIM_PHASE2_WIDTH, "Phase 2 Width (mSec)", m_fPhase2Width_mSec);
	AO_DDX_Float(pDX, IDC_EDIT_STIM_PHASE1_AMP, "Phase 1 Amp. (mAmp)", m_fPhase1Amp_mAmp);
	AO_DDX_Float(pDX, IDC_EDIT_STIM_PHASE2_AMP, "Phase 2 Amp. (mAmp)", m_fPhase2Amp_mAmp);
}

BEGIN_MESSAGE_MAP(CDlgDigitalStimSetup, CDialogEx)
	ON_BN_CLICKED(IDC_BUTTON_APPLY, OnApply)
	ON_BN_CLICKED(IDC_BUTTON_START, OnStart)
END_MESSAGE_MAP()

////////////////////////////////////////////////////////////////////////////////////////////////
// CDlgDigitalStimSetup message handlers

void CDlgDigitalStimSetup::OnOK()
{
	OnApply();

	if (!m_bError)
		CDialogEx::OnOK();
}

void CDlgDigitalStimSetup::OnApply()
{
	m_bError = !UpdateData(TRUE);
	if (m_bError) return;

	if (eAO_OK != SetStimulationParameters(m_fPhase1Amp_mAmp, m_fPhase1Width_mSec, m_fPhase2Amp_mAmp, m_fPhase2Width_mSec,
		m_nFreq_Hz, m_fDuration_Sec, m_nReturnChannel, m_nContactID, m_fPhase1Delay_mSec, m_fPhase2Delay_mSec))
	{
		ShowSystemSDKError();
		m_bError = true;
		return;
	}
}

void CDlgDigitalStimSetup::OnStart()
{
	m_bError = !UpdateData(TRUE);
	if (m_bError) return;

	if (eAO_OK != StartDigitalStimulation(m_nContactID, m_fPhase1Delay_mSec, m_fPhase1Amp_mAmp, m_fPhase1Width_mSec,
		m_fPhase2Delay_mSec, m_fPhase2Amp_mAmp, m_fPhase2Width_mSec, m_nFreq_Hz, m_fDuration_Sec, m_nReturnChannel))
	{
		ShowSystemSDKError();
		m_bError = true;
		return;
	}
}

CString CDlgDigitalStimSetup::GetSystemSDKError()
{
	char sError[1000] = {0};
	int  nErrorCount  = 0;

	ErrorHandlingfunc(&nErrorCount, sError, 1000);

	return CString(sError);
}

void CDlgDigitalStimSetup::ShowSystemSDKError()
{
	CString sError = GetSystemSDKError();
	AfxMessageBox(sError, MB_OK);
}

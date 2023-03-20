#pragma once

///////////////////////////////////////////////////////////////////////////
// CDlgDigitalStimSetup dialog

class CDlgDigitalStimSetup : public CDialogEx
{
	DECLARE_DYNAMIC(CDlgDigitalStimSetup)

public:
	CDlgDigitalStimSetup(CWnd* pParent = NULL);
	virtual ~CDlgDigitalStimSetup();

	enum { IDD = IDD_DIALOG_STIM_SETUP };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);
	virtual void OnOK();
	afx_msg void OnApply();
	afx_msg void OnStart();
	DECLARE_MESSAGE_MAP()

private:
	bool  m_bError;
	int   m_nContactID;
	int   m_nReturnChannel;
	float m_fDuration_Sec;
	int   m_nFreq_Hz;
	float m_fPhase1Delay_mSec;
	float m_fPhase2Delay_mSec;
	float m_fPhase1Width_mSec;
	float m_fPhase2Width_mSec;
	float m_fPhase1Amp_mAmp;
	float m_fPhase2Amp_mAmp;

	CString GetSystemSDKError();
	void ShowSystemSDKError();
};

#pragma once

#include "AOTypes.h"

///////////////////////////////////////////////////////////////////////////
// CDlgWaveForm dialog

class CDlgWaveForm : public CDialogEx
{
	DECLARE_DYNAMIC(CDlgWaveForm)

public:
	CDlgWaveForm(CWnd* pParent = NULL);
	virtual ~CDlgWaveForm();

	enum { IDD = IDD_DIALOG_WAVE_FORMS };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);
	virtual BOOL OnInitDialog();
	afx_msg void OnBrowse();
	afx_msg void OnLoad();
	afx_msg void OnLoadBiggestWave();
	DECLARE_MESSAGE_MAP()

private:
	CEdit m_editName;
	CEdit m_editSamplesFilePath;
	int   m_nDownSampleFactor;

	int  GetWaveFormSamplesCount();
	bool GetWaveFormSamples(int16 *pSamples, int nSamples);

	CString GetSystemSDKError();
	void ShowSystemSDKError();
};

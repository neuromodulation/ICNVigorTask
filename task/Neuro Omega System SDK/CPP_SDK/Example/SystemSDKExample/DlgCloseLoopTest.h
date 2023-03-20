#pragma once

///////////////////////////////////////////////////////////////////////////
// CDlgCloseLoopTest dialog

class CDlgCloseLoopTest : public CDialogEx
{
	DECLARE_DYNAMIC(CDlgCloseLoopTest)

public:
	CDlgCloseLoopTest(CWnd* pParent = NULL);
	virtual ~CDlgCloseLoopTest();

	enum { IDD = IDD_DIALOG_CLOSE_LOOP_TEST };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);
	virtual BOOL OnInitDialog();
	afx_msg void OnBnClickedRunTest();
	DECLARE_MESSAGE_MAP()

private:
	CButton m_btnTest;

	int  m_nDOChannelID;
	int  m_nDOMask;
	int  m_nDIChannelID;
	int  m_nDIMask;
	int  m_nStimContactID;
	int  m_nTestLoops;
	bool m_bTestRunning;
	bool m_bStopTest;

	void CloseLoopTest();

	CString GetSystemSDKError();
	void ShowSystemSDKError();
};

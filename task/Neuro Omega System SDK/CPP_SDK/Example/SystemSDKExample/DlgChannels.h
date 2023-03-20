#pragma once

///////////////////////////////////////////////////////////////////////////
// CDlgChannels dialog

class CDlgChannels : public CDialogEx
{
	DECLARE_DYNAMIC(CDlgChannels)

public:
	CDlgChannels(CWnd* pParent = NULL);
	virtual ~CDlgChannels();

	enum { IDD = IDD_DIALOG_CHANNELS };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);
	virtual BOOL OnInitDialog();
	DECLARE_MESSAGE_MAP()

private:
	CListCtrl m_ctrlChannelsList;

	bool WaitForAllChannels();
	void LoadChannels();

	CString GetSystemSDKError();
	void ShowSystemSDKError();
};

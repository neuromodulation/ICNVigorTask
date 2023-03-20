// DlgChannels.cpp : implementation file
//

#include "stdafx.h"
#include "SystemSDKExample.h"
#include "DlgChannels.h"
#include "afxdialogex.h"
#include "AOSystemAPI.h"

#define LIST_CHANNEL_ID_COL   0
#define LIST_CHANNEL_NAME_COL 1

///////////////////////////////////////////////////////////////////////////
// CDlgChannels dialog

IMPLEMENT_DYNAMIC(CDlgChannels, CDialogEx)

CDlgChannels::CDlgChannels(CWnd* pParent /*=NULL*/)
	: CDialogEx(CDlgChannels::IDD, pParent)
{
}

CDlgChannels::~CDlgChannels()
{
}

void CDlgChannels::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);

	DDX_Control(pDX, IDC_LIST_CHANNELS, m_ctrlChannelsList);
}

BEGIN_MESSAGE_MAP(CDlgChannels, CDialogEx)
END_MESSAGE_MAP()

////////////////////////////////////////////////////////////////////////////////////////////////
// CDlgChannels message handlers

BOOL CDlgChannels::OnInitDialog()
{
	BOOL bRes = CDialogEx::OnInitDialog();

	CRect rcList;
	m_ctrlChannelsList.GetClientRect(rcList);

	// Add Channel ID column
	m_ctrlChannelsList.InsertColumn(LIST_CHANNEL_ID_COL, "Channel ID", LVCFMT_LEFT, 80);

	// Add Channel Name column
	m_ctrlChannelsList.InsertColumn(LIST_CHANNEL_NAME_COL, "Name", LVCFMT_LEFT, rcList.Width() - 80 - 1);

	unsigned long extStyle =  LVS_EX_FULLROWSELECT
							| LVS_EX_GRIDLINES;
	m_ctrlChannelsList.SetExtendedStyle(extStyle);

	if (WaitForAllChannels())
		LoadChannels();

	return bRes;
}

bool CDlgChannels::WaitForAllChannels()
{
	uint32 uChannelsCountPrev = 0;
	if (GetChannelsCount(&uChannelsCountPrev) != eAO_OK)
	{
		ShowSystemSDKError();
		return false;
	}

	uint32 uChannelsCountCurr = 0;
	do
	{
		Sleep(500);
		if (GetChannelsCount(&uChannelsCountCurr) != eAO_OK)
		{
			ShowSystemSDKError();
			return false;
		}

		if (uChannelsCountCurr == uChannelsCountPrev)
			break; // No more channels

		uChannelsCountPrev = uChannelsCountCurr;
	} while (1);

	return true;
}

void CDlgChannels::LoadChannels()
{
	uint32 uChannelsCount = 0;
	if (GetChannelsCount(&uChannelsCount) != eAO_OK)
	{
		ShowSystemSDKError();
		return;
	}

	if (uChannelsCount == 0)
		return;

	SInformation *pChannelsInfo = new SInformation[uChannelsCount];

	if (GetAllChannels(pChannelsInfo, uChannelsCount) != eAO_OK)
	{
		ShowSystemSDKError();
	}
	else
	{
		for (int i=0; i<uChannelsCount; i++)
		{
			int nItem = m_ctrlChannelsList.InsertItem(m_ctrlChannelsList.GetItemCount(), "");
			if (nItem != -1)
			{
				CString sTxt = __T("");
				sTxt.Format("%d", pChannelsInfo[i].channelID);
				m_ctrlChannelsList.SetItemText(nItem, LIST_CHANNEL_ID_COL, sTxt);
				m_ctrlChannelsList.SetItemText(nItem, LIST_CHANNEL_NAME_COL, CString(pChannelsInfo[i].channelName));
				m_ctrlChannelsList.SetItemData(nItem, pChannelsInfo[i].channelID);
			}
		}
	}

	delete[] pChannelsInfo;
}

CString CDlgChannels::GetSystemSDKError()
{
	char sError[1000] = {0};
	int  nErrorCount  = 0;

	ErrorHandlingfunc(&nErrorCount, sError, 1000);

	return CString(sError);
}

void CDlgChannels::ShowSystemSDKError()
{
	CString sError = GetSystemSDKError();
	AfxMessageBox(sError, MB_OK);
}

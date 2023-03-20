// DlgWaveForm.cpp : implementation file
//

#include "stdafx.h"
#include "SystemSDKExample.h"
#include "DlgWaveForm.h"
#include "afxdialogex.h"
#include "AOddx.h"
#include "AOSystemAPI.h"

#include <fstream>
#include <iostream>
#include <iomanip>

using std::cout;
using std::endl;

////////////////////////////////////////////////////////////////////////////////////////////////
// CDlgWaveForm dialog

IMPLEMENT_DYNAMIC(CDlgWaveForm, CDialogEx)

CDlgWaveForm::CDlgWaveForm(CWnd* pParent /*=NULL*/)
	: CDialogEx(CDlgWaveForm::IDD, pParent)
{
	m_nDownSampleFactor = 1;
}

CDlgWaveForm::~CDlgWaveForm()
{
}

void CDlgWaveForm::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	
	DDX_Control(pDX, IDC_EDIT_WAVEFORM_NAME, m_editName);
	DDX_Control(pDX, IDC_EDIT_WAVEFORM_SAMPLES, m_editSamplesFilePath);

	AO_DDX_Int(pDX, IDC_EDIT_WAVEFORM_DSF, "Down Sample Factor", m_nDownSampleFactor);
}

BEGIN_MESSAGE_MAP(CDlgWaveForm, CDialogEx)
	ON_BN_CLICKED(IDC_BUTTON_WAVEFORM_BROWSE, OnBrowse)
	ON_BN_CLICKED(IDC_BUTTON_WAVEFORM_LOAD, OnLoad)
	ON_BN_CLICKED(IDC_BUTTON_TEST, OnLoadBiggestWave)
END_MESSAGE_MAP()

////////////////////////////////////////////////////////////////////////////////////////////////
// CDlgWaveForm message handlers

BOOL CDlgWaveForm::OnInitDialog()
{
	BOOL bRet = CDialogEx::OnInitDialog();

	m_editName.SetWindowText("TestWave");

	return bRet;
}

void CDlgWaveForm::OnBrowse()
{
	CFileDialog dlgFile(TRUE, "txt", NULL, OFN_HIDEREADONLY|OFN_NOCHANGEDIR,
		"Txt Files (*.txt)|*.txt|All Files (*.*)|*.*||");

	dlgFile.m_ofn.lpstrTitle = (LPSTR)"Open Wave Form Samples File";

	CString sFullPathFileName = __T("");
	m_editSamplesFilePath.GetWindowText(sFullPathFileName);

	dlgFile.m_ofn.lpstrFile = sFullPathFileName.GetBuffer(MAX_PATH);
	dlgFile.m_ofn.nMaxFile  = MAX_PATH;

	if (dlgFile.DoModal() == IDOK)
	{
		m_editSamplesFilePath.SetWindowText( dlgFile.GetPathName() );
	}
}

void CDlgWaveForm::OnLoad()
{
	if (!UpdateData(TRUE))
		return;

	CString sWaveName = __T("");
	m_editName.GetWindowText(sWaveName);

	int nSamples = GetWaveFormSamplesCount();
	if (nSamples == 0) return;

	int16 *pSamples = new int16[nSamples];
	do
	{
		bool bRes = GetWaveFormSamples(pSamples, nSamples);
		if (!bRes) break;

		if (eAO_OK != LoadWaveToEmbedded(pSamples, nSamples, m_nDownSampleFactor, sWaveName.GetBuffer()))
			ShowSystemSDKError();
		else
			MessageBox("Load wave done successfully");
	} while (false);

	delete[] pSamples;
}

int CDlgWaveForm::GetWaveFormSamplesCount()
{
	CString sFullPathFileName = __T("");
	m_editSamplesFilePath.GetWindowText(sFullPathFileName);

	std::ifstream inFile;
	inFile.open(sFullPathFileName.GetBuffer());

	if (!inFile)
	{
		ShowError(this, CString("Can't open wave form file."));
		return 0;
	}

	long nSample  = 0;
	int  nSamples = 0;
	while (!inFile.eof())
	{
		inFile >> nSample;
		nSamples++;
	}

	inFile.close();
	return nSamples;
}

bool CDlgWaveForm::GetWaveFormSamples(int16 *pSamples, int nSamples)
{
	CString sFullPathFileName = __T("");
	m_editSamplesFilePath.GetWindowText(sFullPathFileName);

	std::ifstream inFile;
	inFile.open(sFullPathFileName.GetBuffer());

	if (!inFile)
	{
		ShowError(this, CString("Can't open wave form file."));
		return false;
	}

	long nSample = 0;
	int  nIdx    = 0;
	while (!inFile.eof() && nIdx < nSamples)
	{
		inFile >> nSample;
		pSamples[nIdx++] = (int16)nSample;
	}

	inFile.close();
	return true;
}

void CDlgWaveForm::OnLoadBiggestWave()
{
	if (!UpdateData(TRUE))
		return;

	CString sWaveName = __T("");
	m_editName.GetWindowText(sWaveName);

	// Test 8000000
	int    nSamples = 8000000;
	int16 *pSamples = new int16[nSamples];
	int    nDelta   = 10;
	int    nSample  = 0;
	for (int i=0; i<nSamples; i++)
	{
		pSamples[i] = nSample;

		if (nSample <= -1000 || nSample >= 1000)
			nDelta *= -1; // Reverse sign

		nSample = nSample + nDelta;
	}

	if (eAO_OK != LoadWaveToEmbedded(pSamples, nSamples, m_nDownSampleFactor, sWaveName.GetBuffer()))
		ShowSystemSDKError();
	else
		MessageBox("LoadWaveToEmbedded Success");

	delete[] pSamples;
}

CString CDlgWaveForm::GetSystemSDKError()
{
	char sError[1000] = {0};
	int  nErrorCount  = 0;

	ErrorHandlingfunc(&nErrorCount, sError, 1000);

	return CString(sError);
}

void CDlgWaveForm::ShowSystemSDKError()
{
	CString sError = GetSystemSDKError();
	AfxMessageBox(sError, MB_OK);
}

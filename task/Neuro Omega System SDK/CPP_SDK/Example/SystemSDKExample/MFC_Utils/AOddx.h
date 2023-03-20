#ifndef __AODDX_H__
#define __AODDX_H__

#include "AOTypes.h"

void ShowError(CWnd *pWnd, CString & sError, CString sTitle="");
void ShowErrorBalloonTip(CWnd *pWnd, wchar_t *pError);

void AO_DDX_Int(CDataExchange* pDX, int nIDC, CString sName, int & value);
void AO_DDX_MinInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, int & value);
void AO_DDX_MaxInt(CDataExchange* pDX, int nIDC, CString sName, int nMax, int & value);
void AO_DDX_MinMaxInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, int nMax, int & value);

void AO_DDX_UInt(CDataExchange* pDX, int nIDC, CString sName, uint32 & value);
void AO_DDX_MinUInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, uint32 & value);
void AO_DDX_MaxUInt(CDataExchange* pDX, int nIDC, CString sName, int nMax, uint32 & value);
void AO_DDX_MinMaxUInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, int nMax, uint32 & value);

void AO_DDX_Float(CDataExchange* pDX, int nIDC, CString sName, float & value);
void AO_DDX_MinFloat(CDataExchange* pDX, int nIDC, CString sName, float dMin, float & value);
void AO_DDX_MaxFloat(CDataExchange* pDX, int nIDC, CString sName, float dMax, float & value);
void AO_DDX_MinMaxFloat(CDataExchange* pDX, int nIDC, CString sName, float dMin, float dMax, float & value);

void AO_DDX_Double(CDataExchange* pDX, int nIDC, CString sName, double & value);
void AO_DDX_MinDouble(CDataExchange* pDX, int nIDC, CString sName, double dMin, double & value);
void AO_DDX_MaxDouble(CDataExchange* pDX, int nIDC, CString sName, double dMax, double & value);
void AO_DDX_MinMaxDouble(CDataExchange* pDX, int nIDC, CString sName, double dMin, double dMax, double & value);

#endif

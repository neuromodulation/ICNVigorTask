#include "stdafx.h"
#include "AOddx.h"

#include <math.h>

//////////////////////////////////////////////////////////////////////////////////
// Helper Functions

bool StringToNumber(const char *buffer,int* Retvalue)
{
   bool ret=false;
   int result = 0;
   int startIndex = 0;
   int negativeNumber = 0;
   int i, digit;
 
   if(buffer[0] == '-')
   {
         negativeNumber = 1;
         startIndex = 1;
   }
   for(i = startIndex; i < strlen(buffer); i++)
   {
      ret=true;
	  if(buffer[i] >= '0' && buffer[i] <= '9')
      {
         digit = buffer[i] - '0';
         result = result * 10 + digit;
      }
      else
         return 0;
   }

   if(negativeNumber == 1)
      result *= -1;
    *Retvalue =result;

	return ret;
}

bool StringToFloat(const char *buffer,float* Retvalue)
{
	CString sText(buffer);
	CString sLeft  = sText;
	CString sRight = __T("");

	int nFloatingPointIdx = sText.Find('.');
	if (nFloatingPointIdx == 0) return FALSE;
	if (nFloatingPointIdx != -1)
	{
		sLeft = sText.Left(nFloatingPointIdx);
		// if floating point not at the end.
		if (nFloatingPointIdx < sText.GetLength()-1) sRight = sText.Mid(nFloatingPointIdx+1, sText.GetLength()-nFloatingPointIdx);
	}

	int nLeft  = 0;
	int nRight = 0;

	if (!StringToNumber(sLeft, &nLeft)) return FALSE;
	if (!sRight.IsEmpty() && (!StringToNumber(sRight, &nRight) || nRight<0)) return FALSE;

	*Retvalue = abs(nLeft);
	if (!sRight.IsEmpty())
	{
		float dFactor = pow(10., sRight.GetLength());
		float dRight  = (float)nRight;
		*Retvalue += dRight/dFactor;
	}

	if (buffer[0] == '-') *Retvalue *= -1;

	return TRUE;
}

bool StringToDouble(const char *buffer,double* Retvalue)
{
	CString sText(buffer);
	CString sLeft  = sText;
	CString sRight = __T("");

	int nFloatingPointIdx = sText.Find('.');
	if (nFloatingPointIdx == 0) return FALSE;
	if (nFloatingPointIdx != -1)
	{
		sLeft = sText.Left(nFloatingPointIdx);
		// if floating point not at the end.
		if (nFloatingPointIdx < sText.GetLength()-1) sRight = sText.Mid(nFloatingPointIdx+1, sText.GetLength()-nFloatingPointIdx);
	}

	int nLeft  = 0;
	int nRight = 0;

	if (!StringToNumber(sLeft, &nLeft)) return FALSE;
	if (!sRight.IsEmpty() && (!StringToNumber(sRight, &nRight) || nRight<0)) return FALSE;

	*Retvalue = abs(nLeft);
	if (!sRight.IsEmpty())
	{
		double dFactor = pow(10., sRight.GetLength());
		double dRight  = (double)nRight;
		*Retvalue += dRight/dFactor;
	}

	if (buffer[0] == '-') *Retvalue *= -1;

	return TRUE;
}

//////////////////////////////////////////////////////////////////////////////////

void ShowError(CWnd *pWnd, CString & sError, CString sTitle)
{
	/*
	EDITBALLOONTIP ebt; 
    LPWSTR pszText = CA2W(sError); 
    LPWSTR pszTitle = L"Error"; 
    ebt.cbStruct = sizeof(EDITBALLOONTIP); 
    ebt.pszText = pszText; 
    ebt.pszTitle = pszTitle; 
	ebt.ttiIcon = TTI_ERROR; 
	Edit_ShowBalloonTip(*pWnd, &ebt);
	*/
	
	CWnd *pParent = pWnd->GetParent();
	if (pParent != NULL)
	{
		if (sTitle.IsEmpty())
			pParent->GetWindowText(sTitle);
		pParent->MessageBox(sError, sTitle, MB_OK|MB_ICONERROR);
	}
	else
	{
		AfxMessageBox(sError, MB_OK|MB_ICONERROR);
	}
}

void ShowErrorBalloonTip(CWnd *pWnd, wchar_t *pError)
{
    EDITBALLOONTIP bt;
  
    bt.cbStruct = sizeof(EDITBALLOONTIP);
    bt.pszTitle = L"Error";
    bt.pszText  = pError;
    bt.ttiIcon  = TTI_ERROR;
	Edit_ShowBalloonTip(*pWnd, &bt);
}

void AO_DDX_Int(CDataExchange* pDX, int nIDC, CString sName, int & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToNumber(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid integer number for [%s].", sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MinInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, int & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToNumber(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid integer number for [%s].", sName);
	}
	else if (value < nMin)
	{
		sError.Format("Please enter an integer number bigger or equal to %d for [%s].", nMin, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MaxInt(CDataExchange* pDX, int nIDC, CString sName, int nMax, int & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToNumber(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid integer number for [%s].", sName);
	}
	else if (value > nMax)
	{
		sError.Format("Please enter an integer number less or equal to %d for [%s].", nMax, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MinMaxInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, int nMax, int & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToNumber(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid integer number for [%s].", sName);
	}
	else if (value < nMin || value > nMax)
	{
		sError.Format("Please enter an integer number between %d and %d for [%s].", nMin, nMax, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

		//pWnd->SetFocus();
		//pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_UInt(CDataExchange* pDX, int nIDC, CString sName, uint32 & value)
{
	int nValue = value;
	AO_DDX_Int(pDX, nIDC, sName, nValue);

	if (!pDX->m_bSaveAndValidate) return;

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	if (nValue < 0)
	{
		sError.Format("Please enter a positive integer number for [%s].", sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
	else
		value = (uint32)nValue;
}

void AO_DDX_MinUInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, uint32 & value)
{
	int nValue = value;
	AO_DDX_MinInt(pDX, nIDC, sName, nMin, nValue);

	if (!pDX->m_bSaveAndValidate) return;

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	if (nValue < 0)
	{
		sError.Format("Please enter a positive integer number for [%s].", sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
	else
		value = (uint32)nValue;
}

void AO_DDX_MaxUInt(CDataExchange* pDX, int nIDC, CString sName, int nMax, uint32 & value)
{
	int nValue = value;
	AO_DDX_MaxInt(pDX, nIDC, sName, nMax, nValue);

	if (!pDX->m_bSaveAndValidate) return;

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	if (nValue < 0)
	{
		sError.Format("Please enter a positive integer number for [%s].", sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
	else
		value = (uint32)nValue;
}

void AO_DDX_MinMaxUInt(CDataExchange* pDX, int nIDC, CString sName, int nMin, int nMax, uint32 & value)
{
	int nValue = value;
	AO_DDX_MinMaxInt(pDX, nIDC, sName, nMin, nMax, nValue);

	if (!pDX->m_bSaveAndValidate) return;

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	if (nValue < 0)
	{
		sError.Format("Please enter a positive integer number for [%s].", sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
	else
		value = (uint32)nValue;
}

void AO_DDX_Float(CDataExchange* pDX, int nIDC, CString sName, float & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToFloat(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MinFloat(CDataExchange* pDX, int nIDC, CString sName, float dMin, float & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToFloat(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}
	else if (value < dMin)
	{
		sError.Format("Please enter an real number bigger or equal to %.3f for [%s].", dMin, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MaxFloat(CDataExchange* pDX, int nIDC, CString sName, float dMax, float & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToFloat(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}
	else if (value > dMax)
	{
		sError.Format("Please enter an real number less or equal to %.3f for [%s].", dMax, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MinMaxFloat(CDataExchange* pDX, int nIDC, CString sName, float dMin, float dMax, float & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToFloat(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}
	else if (value < dMin || value > dMax)
	{
		sError.Format("Please enter an real number between %.3f and %.3f for [%s].", dMin, dMax, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_Double(CDataExchange* pDX, int nIDC, CString sName, double & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToDouble(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MinDouble(CDataExchange* pDX, int nIDC, CString sName, double dMin, double & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToDouble(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}
	else if (value < dMin)
	{
		sError.Format("Please enter an real number bigger or equal to %.3f for [%s].", dMin, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MaxDouble(CDataExchange* pDX, int nIDC, CString sName, double dMax, double & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToDouble(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}
	else if (value > dMax)
	{
		sError.Format("Please enter an real number less or equal to %.3f for [%s].", dMax, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

void AO_DDX_MinMaxDouble(CDataExchange* pDX, int nIDC, CString sName, double dMin, double dMax, double & value)
{
	if (!pDX->m_bSaveAndValidate)
	{
		DDX_Text(pDX, nIDC, value);
		return;
	}

	CWnd *pWnd = pDX->m_pDlgWnd->GetDlgItem(nIDC);
	if (pWnd == NULL) return;

	CString sError = __T("");
	CString sText  = __T("");
	pWnd->GetWindowText(sText);

	if (StringToDouble(sText, &value) == FALSE)
	{
		sError.Format("Please enter a valid real number for [%s].", sName);
	}
	else if (value < dMin || value > dMax)
	{
		sError.Format("Please enter an real number between %.3f and %.3f for [%s].", dMin, dMax, sName);
	}

	if (!sError.IsEmpty())
	{
		ShowError(pWnd, sError);

	//	pWnd->SetFocus();
	//	pDX->PrepareCtrl(nIDC);
		pDX->Fail();
	}
}

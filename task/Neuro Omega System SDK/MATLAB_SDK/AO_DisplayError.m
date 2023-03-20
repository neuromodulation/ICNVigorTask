function AO_DisplayError( )

[Result, ErrorCount, LastError] = AO_GetError();
if (Result == 0)
	disp(LastError);
end
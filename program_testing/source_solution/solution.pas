var n,n2,n5:longint;
begin
 n2:=0;
 n5:=0;
 read(n);
 while n mod 2=0 do
 begin
 n:= n div 2 ;
 inc(n2);
 end;
 while n mod 5=0 do
 begin
 n:= n div 5;
 inc(n5);
 end;
 if n>1 then
 writeln('NO')
 else if n5>n2 then
 writeln(n5)
 else
 writeln(n2);
end.
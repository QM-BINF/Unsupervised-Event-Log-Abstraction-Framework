@GOTO start

:add
 @set X=%X%;%1
 @GOTO :eof

:start
@set X=.\dist\ProM-Framework-6.11.121.jar
@set X=%X%;.\dist\ProM-Contexts-6.11.67.jar
@set X=%X%;.\dist\ProM-Models-6.10.43.jar
@set X=%X%;.\dist\ProM-Plugins-6.9.75.jar

@for /R .\lib %%I IN ("*.jar") DO @call :add .\lib\%%~nI.jar

@java^
 -Xmx1G^
 -da^
 -classpath "%X%"^
 -Djava.library.path=.//lib^
 -Djava.system.class.loader=org.processmining.framework.util.ProMClassLoader^
 -Djava.util.Arrays.useLegacyMergeSort=true^
 org.processmining.contexts.uitopia.packagemanager.PMFrame

set X=

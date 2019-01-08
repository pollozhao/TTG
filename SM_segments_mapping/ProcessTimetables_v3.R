#TimetableDir	<- "C:/Users/scottm/Documents/Projects/UK/Freightliner/Timetables/IM_Timetables_New"
#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Freightliner/Timetables"

#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Arriva XC/Timetables"
#TimetableDir	<- "C:/Users/scottm/Documents/Projects/UK/Arriva XC/Timetables/xc-Timetables"

#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/NIR/Timetable Mapping"
#TimetableDir	<- "C:/Users/scottm/Documents/Projects/UK/NIR/Timetable Mapping/Timetables"

MainDir		<- "C:/Users/scottm/Documents/Projects/UK/ATW/Timetable Mapping"
TimetableDir	<- "C:/Users/scottm/Documents/Projects/UK/ATW/Timetable Mapping/Timetables"

#*************************************************************************************
MaxTIPLOCsTimetable	<- 1500000
MaxNumTimetables		<- 100000
#*************************************************************************************

setwd(MainDir)
TimetableFiles	<- list.files(TimetableDir,pattern="*.xml",full.names=TRUE)

numTimetables	<- 0
numTIPLOCs		<- 0
numTIPLOCs2		<- 0

TimetableNumber	<- integer(MaxTIPLOCsTimetable)
Headcode		<- character(MaxTIPLOCsTimetable)
DaysRun		<- character(MaxTIPLOCsTimetable)
Time			<- character(MaxTIPLOCsTimetable)
TIPLOC		<- character(MaxTIPLOCsTimetable)
TIPLOC_Code		<- character(MaxTIPLOCsTimetable)
TIPLOC_Num		<- integer(MaxTIPLOCsTimetable)
LineCode		<- character(MaxTIPLOCsTimetable)
Platform		<- character(MaxTIPLOCsTimetable)

CurrHeadcode	<- character(MaxNumTimetables)
CurrDaysRun		<- character(MaxNumTimetables)
WorkStart		<- character(MaxNumTimetables)
WorkEnd		<- character(MaxNumTimetables)
StartDate		<- character(MaxNumTimetables)
EndDate		<- character(MaxNumTimetables)
StartTIPLOC		<- character(MaxNumTimetables)
EndTIPLOC		<- character(MaxNumTimetables)


for(i in TimetableFiles){
	TimetableXML	<- read.table(i,strip.white=TRUE,header=FALSE,quote="#",as.is=T,fill=T,sep="\t")
	numRowsData		<- nrow(TimetableXML)
	for(j in 1:numRowsData){
		x	<- unlist(strsplit(TimetableXML[j,],"\""))
		if(x[1] == "<TrainHeader TSDBUID="){
			numTimetables	<- numTimetables + 1
			CurrHeadcode[numTimetables]		<- x[4]
			CurrDaysRun[numTimetables]		<- x[6]			
			StartDate[numTimetables]		<- x[22]
			EndDate[numTimetables]			<- x[24]
			WorkStart[numTimetables]		<- x[12]
			WorkEnd[numTimetables]			<- x[14]
			StartTIPLOC[numTimetables]		<- x[8]
			EndTIPLOC[numTimetables]		<- x[10]
		}
		if(x[1] == "<TrainEvent LocationTiploc="){
			if(numTIPLOCs < MaxTIPLOCsTimetable){
				numTIPLOCs		<- numTIPLOCs + 1
				numTIPLOCs2		<- numTIPLOCs2 + 1
				TimetableNumber[numTIPLOCs]	<- numTimetables
				TIPLOC_Code[numTIPLOCs]		<- x[2]
				Headcode[numTIPLOCs]	<- CurrHeadcode[numTimetables]
				DaysRun[numTIPLOCs]	<- CurrDaysRun[numTimetables]
				Time[numTIPLOCs]		<- x[4] 
				TIPLOC[numTIPLOCs]	<- gsub("&amp;","&",x[12])
				Platform[numTIPLOCs]	<- x[10]
				LineCode[numTIPLOCs]	<- x[8]
			} else {
				numTIPLOCs2		<- numTIPLOCs2 + 1
			}
		}		
	}
}
TimetableNumber	<- TimetableNumber[1:numTIPLOCs]
Headcode		<- Headcode[1:numTIPLOCs]
DaysRun		<- DaysRun[1:numTIPLOCs]
TIPLOC		<- TIPLOC[1:numTIPLOCs]
TIPLOC_Code		<- TIPLOC_Code[1:numTIPLOCs]
Time			<- Time[1:numTIPLOCs]
Platform		<- Platform[1:numTIPLOCs]
LineCode		<- LineCode[1:numTIPLOCs]

CurrHeadcode	<- CurrHeadcode[1:numTimetables]
CurrDaysRun		<- CurrDaysRun[1:numTimetables]		
StartDate		<- StartDate[1:numTimetables]
EndDate		<- EndDate[1:numTimetables]
WorkStart		<- WorkStart[1:numTimetables]
WorkEnd		<- WorkEnd[1:numTimetables]
StartTIPLOC		<- StartTIPLOC[1:numTimetables]
EndTIPLOC		<- EndTIPLOC[1:numTimetables]


TimetableData	<- data.frame(TimetableNumber,Headcode,TIPLOC,TIPLOC_Code,Time,LineCode,Platform,rep(NA,numTIPLOCs),rep("-",numTIPLOCs))
write.table(TimetableData,file="Timetable_TIPLOCs.txt",sep="\t",row.names=FALSE,col.names=FALSE,quote=FALSE)
TimetableData	<- data.frame(1:numTimetables,CurrHeadcode,CurrDaysRun,StartDate,EndDate,WorkStart,WorkEnd,StartTIPLOC,EndTIPLOC)
write.table(TimetableData,file="Timetables.txt",sep="\t",row.names=FALSE,col.names=FALSE,quote=FALSE)



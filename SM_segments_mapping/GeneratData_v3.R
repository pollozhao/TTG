#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Freightliner/Timetables"
#SegDir		<- "C:/SourceControl/Sites/UK/Freightliner/Data/Segments"

#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Arriva XC/Timetables"
#SegDir		<- "C:/Users/scottm/Documents/Projects/UK/Arriva XC/Segments/Segments All"

#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/NIR/Timetable Mapping"
#SegDir		<- "C:/SourceControl/Sites/UK/NIR/Data/Segments"

MainDir		<- "C:/Users/scottm/Documents/Projects/UK/ATW/Timetable Mapping"
SegDir		<- "C:/SourceControl/Sites/UK/ArrivaTW/Data/Segments"

TIPLOCReport	<- FALSE

#*****************************************************************************

setwd(MainDir)
subDir	<- "Mapping Data"
Mappings_df		<- read.table("SegmentMappings_R.txt",strip.white=TRUE,header=FALSE,quote="\"",as.is=T,fill=T,sep="\t",comment="#")
SegmentNames	<- sort(unique(c(Mappings_df[,1],Mappings_df[,2])))
SegmentNames	<- SegmentNames[SegmentNames != ""]
dir.create(file.path(MainDir, subDir), showWarnings = FALSE)

maxNumTIPLOCs	<- 50000
numTIPLOCs		<- 0

TIPLOC_List		<- character(maxNumTIPLOCs)
File_List		<- character(maxNumTIPLOCs)
TIPLOCDist_List	<- numeric(maxNumTIPLOCs)
SegmentLength	<- numeric(length(SegmentNames))

for (j in 1:length(SegmentNames)){
	SegmentData		<- read.table(paste(SegDir,"/",SegmentNames[j],".seg",sep=""),skip=2,fill=TRUE,sep="\t",comment.char="#",quote="\"",as.is=T,strip.white=TRUE)
	FileTIPLOCs		<- SegmentData$V5[SegmentData$V4 == "ST" & !is.na(SegmentData$V4)]
	TIPLOCDist		<- SegmentData$V1[SegmentData$V4 == "ST" & !is.na(SegmentData$V4)]
	numTIPLOCs		<- numTIPLOCs + length(FileTIPLOCs)
	if(length(FileTIPLOCs) > 0){
		TIPLOC_List[(numTIPLOCs-length(FileTIPLOCs)+1):numTIPLOCs]		<- FileTIPLOCs
		File_List[(numTIPLOCs-length(FileTIPLOCs)+1):numTIPLOCs]		<- SegmentNames[j]
		TIPLOCDist_List[(numTIPLOCs-length(FileTIPLOCs)+1):numTIPLOCs]	<- as.numeric(TIPLOCDist)
	}
	SegmentLength[j]	<- max(SegmentData$V1)
}
TIPLOC_List		<- TIPLOC_List[1:numTIPLOCs]
File_List		<- File_List[1:numTIPLOCs]
TIPLOCDist_List	<- TIPLOCDist_List[1:numTIPLOCs]

TIPLOCsUnique	<- sort(unique(TIPLOC_List))
TIPLOC_df		<- data.frame()
maxFiles		<- max(table(TIPLOC_List))
TIPLOCFileId_Dist	<- matrix(data=NA,nrow=length(TIPLOCsUnique),ncol=length(SegmentNames))

for(i in 1:length(TIPLOCsUnique)){
	#for some reason some files have the same TIPLOC appearing twice, hence the unique below
	Files1	<- unique(File_List[TIPLOC_List == TIPLOCsUnique[i]])
	Dist		<- TIPLOCDist_List[TIPLOC_List == TIPLOCsUnique[i]]
	Files1	<- match(Files1,SegmentNames)
	for(j in 1:length(Files1)){TIPLOCFileId_Dist[i,Files1[j]]	<- Dist[j]}	
	Files2	<- as.integer(rep(NA,maxFiles))
	Files2[1:length(Files1)]	<- Files1
	TIPLOC_df	<- rbind(TIPLOC_df,data.frame(i,TIPLOCsUnique[i],length(Files1),t(Files2),stringsAsFactors=FALSE))  
}

setwd(paste(MainDir,"/",subDir,sep=""))
SegmentNames	<-gsub(".seg","",SegmentNames)
names(TIPLOC_df)[1:4]=c("Index","Name","Number files","Files")
write.table(TIPLOC_df,file="TIPLOCS.txt",sep="\t",row.names=FALSE,quote=FALSE)
df2	<- data.frame(seq(1,length(SegmentNames)),SegmentNames,SegmentLength)
names(df2)=c("Segment Id","Segment name","Length km")
write.table(df2,file="Segments.txt",row.names=FALSE,quote=FALSE,sep="\t")
write.table(TIPLOCFileId_Dist,file="TIPLOC-FileId_DistMatrix.txt",col.names = FALSE, row.names = FALSE,sep="\t")
setwd(MainDir)

#*****************************************************************

Timetables	<- read.table("Timetable_TIPLOCs.txt",strip.white=TRUE,header=FALSE,quote="#",as.is=T,fill=T,sep="\t")
Timetables[,8]	<- match(Timetables[,3],TIPLOC_df$Name)
write.table(Timetables,file="Timetable_TIPLOCs.txt",sep="\t",row.names=FALSE,col.names=FALSE,quote=FALSE)

#*****************************************************************

#Find row index of start and end of each TT
if(TIPLOCReport == TRUE){
	nRowTT		<- nrow(Timetables)
	numTimetables	<- max(Timetables[,1])
	EndTTIndex		<- c(which(diff(Timetables[,1])!=0),length(Timetables[,1]))
	StartTTIndex	<- c(1,EndTTIndex[-numTimetables]+1)
	CompleteTIPLOCs	<- sort(unique(Timetables[,3]))
	BetweenKnown	<- logical(nRowTT)
	numBetweenKnown	<- integer(nRowTT)
	Turnback		<- logical(nRowTT)
	NextTurnback	<- character(nRowTT)
	StoppingLocation	<- logical(nRowTT)
	for(i in 1:numTimetables){
		TIPLOCsCurrTT	<- Timetables[StartTTIndex[i]:EndTTIndex[i],3]
		for(j in 1:(length(TIPLOCsCurrTT)-1)){
				if(TIPLOCsCurrTT[j] == TIPLOCsCurrTT[j+1]){StoppingLocation[StartTTIndex[i]-1+j] = TRUE}
		}
		if(length(TIPLOCsCurrTT) > 3){
			for(j in 1:(length(TIPLOCsCurrTT)-3)){
					if(TIPLOCsCurrTT[j] == TIPLOCsCurrTT[j+3]){
						Turnback[StartTTIndex[i]+j] = TRUE
						NextTurnback[StartTTIndex[i]-1+j]		<- TIPLOCsCurrTT[j]
					}
			}
		}
		TIPLOCNumCurrTT	<- Timetables[StartTTIndex[i]:EndTTIndex[i],8]
		
		KnownTiplocs	<- which(!is.na(TIPLOCNumCurrTT))
		if(length(KnownTiplocs)>0){
			BetweenKnown[(StartTTIndex[i]-1+min(KnownTiplocs)):(StartTTIndex[i]-1+max(KnownTiplocs))]	<- TRUE
		}
	}
	numTIPLOCs		<- length(CompleteTIPLOCs)
	Turnback2		<- logical(numTIPLOCs)
	StoppingLocation2	<- logical(numTIPLOCs)
	KnownTIPLOC2	<- integer(numTIPLOCs)
	BetweenKnown2	<- logical(numTIPLOCs)
	NextTurnback2	<- character(numTIPLOCs)
	TIPLOCCode		<- character(numTIPLOCs)
	for(i in 1:numTIPLOCs){
		TIPLOCCode[i]	<- Timetables[which(Timetables[,3] == CompleteTIPLOCs[i])[1],4]
		if(any(StoppingLocation[Timetables[,3] == CompleteTIPLOCs[i]] == TRUE)){StoppingLocation2[i] <- TRUE}
		if(any(Turnback[Timetables[,3] == CompleteTIPLOCs[i]] == TRUE)){Turnback2[i] <- TRUE}
		if(any(BetweenKnown[Timetables[,3] == CompleteTIPLOCs[i]] == TRUE)){BetweenKnown2[i] <- TRUE}
		KnownTIPLOC2[i] <- Timetables[,8][Timetables[,3] == CompleteTIPLOCs[i]][1]
	}
	TIPLOC_df	<- data.frame(CompleteTIPLOCs,TIPLOCCode,KnownTIPLOC2,BetweenKnown2,StoppingLocation2,Turnback2)
	names(TIPLOC_df)	<- c("Name","TIPLOC Code", "TIPLOC No.","Between known","Stopping location","Turnback")
	write.table(TIPLOC_df,file="TIPLOC_Report.txt",sep="\t",row.names=FALSE,col.names=TRUE,quote=FALSE)
}
#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Freightliner/Timetables"
#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Arriva XC/Timetables"
MainDir		<- "C:/Users/scottm/Documents/Projects/UK/ATW/Timetables"
MainDir		<- "C:/Users/scottm/Documents/Projects/UK/ATW/Timetable Mapping"

#*********************************************************************************

setwd(MainDir)
Timetable	<- read.table("Timetable_TIPLOCs.txt",quote="\"",header=FALSE,as.is=T,fill=T,sep="\t",comment="#")
setwd(paste(MainDir,"/Mapping Data",sep=""))
TIPLOCData	<- read.table("TIPLOCS.txt",quote="\"",header=TRUE,as.is=T,fill=T,sep="\t",comment="#")
TIPLOC_File_Dist	<- read.table("TIPLOC-FileId_DistMatrix.txt",header=FALSE)
NodeDistMatrix	<- read.table("DistMatrix.txt",header=FALSE,sep="\t")
PreviousNode	<- read.table("ShortestPreviousNode.txt",header=FALSE,sep="\t")
SegmentData	<- read.table("Segments.txt",quote="\"",header=TRUE,as.is=T,fill=T,sep="\t",comment="#")

DummySegment	<- data.frame(nrow(SegmentData)+1,"",0)
names(DummySegment)	<- names(SegmentData)
SegmentData	<- rbind(SegmentData,DummySegment)
DummyNodeId	<- nrow(SegmentData)

numTimetables	<- length(table(Timetable[,1]))

#Find row index of start and end of each TT
EndTTIndex		<- c(which(diff(Timetable[,1])!=0),length(Timetable[,1]))
StartTTIndex	<- c(1,EndTTIndex[-numTimetables]+1)

# find the max number of TIPLOCs in a timetable
maxTIPLOCsTT	<- max(EndTTIndex-StartTTIndex)+1
maxNumFiles		<- ncol(TIPLOCData)-3
CostMatrix		<- matrix(data=Inf,nrow=nrow(Timetable),ncol=maxNumFiles)
PreviousRow		<- rep(NA,nrow(Timetable))
PreviousCol		<- matrix(data=NA,nrow=nrow(Timetable),ncol=maxNumFiles)
PathBreak		<- integer(nrow(Timetable))
TIPLOCMapped	<- logical(nrow(Timetable))
NumTIPOCsSegment	<- integer(nrow(Timetable)*3)
TTMappedTIPLOCs	<- matrix(data="",nrow=nrow(Timetable)*3,ncol=29)

MappedTTLen			<- nrow(Timetable)*6
TTNum				<- integer(MappedTTLen)
TTHeadcode			<- character(MappedTTLen)
TTSegments			<- integer(MappedTTLen)
Path				<- integer(maxTIPLOCsTT)
TIPLOCsMapped		<- integer(maxTIPLOCsTT)
SegmentMappedTIPLOC	<- integer(maxTIPLOCsTT)

Path2			<- integer(600)
NextTTStart		<- 1

for(i in 1:numTimetables){
#for(i in 1:10){
	# Get row indices for known TIPLOCs in timetable i
	RowIndex	<- which(is.na(Timetable[StartTTIndex[i]:EndTTIndex[i],8]) == FALSE)+StartTTIndex[i]-1
	Headcode	<- Timetable[StartTTIndex[i],2]
	#Only attempt to map Timetables with 2 or more known TIPLOCs
	ZeroRow	<- rep(0,maxNumFiles)
	if(length(RowIndex)>1){ 
		PreviousRow[RowIndex[2:length(RowIndex)]]	<- RowIndex[1:(length(RowIndex)-1)]
		CostMatrix[RowIndex[1],]	<- ZeroRow
		for(j in 1:(length(RowIndex)-1)){
			CurrentTIPLOC	<- Timetable[RowIndex[j],8]
			NextTIPLOC		<- Timetable[RowIndex[j+1],8]
			if(NextTIPLOC == CurrentTIPLOC){
				CostMatrix[RowIndex[j+1],]	<- CostMatrix[RowIndex[j],]
				PreviousCol[RowIndex[j+1],1:TIPLOCData[NextTIPLOC,3]]	<- 1:TIPLOCData[NextTIPLOC,3]
				PreviousCol[RowIndex[j+1],which(is.na(PreviousCol[RowIndex[j],]))]	<- NA
			} else {
				if(any(CostMatrix[RowIndex[j],] < Inf)){
					for(k in 1:TIPLOCData[CurrentTIPLOC,3]){
						CurrentNode	<- TIPLOCData[CurrentTIPLOC,k+3]
						if(CostMatrix[RowIndex[j],k] < Inf){
							for(l in 1:TIPLOCData[NextTIPLOC,3]){
								NextNode	<- TIPLOCData[NextTIPLOC,l+3]
								if(CurrentNode == NextNode){
									if(TIPLOC_File_Dist[NextTIPLOC,NextNode]>TIPLOC_File_Dist[CurrentTIPLOC,CurrentNode]){
										CostMatrix[RowIndex[j+1],l] <- CostMatrix[RowIndex[j],k]
										PreviousCol[RowIndex[j+1],l]	<- k
										TIPLOCMapped[RowIndex[j]]	<-TRUE
										TIPLOCMapped[RowIndex[j+1]]	<-TRUE
									}
								} else {
									
									if(CostMatrix[RowIndex[j],k]+NodeDistMatrix[CurrentNode,NextNode] < CostMatrix[RowIndex[j+1],l]){
										CostMatrix[RowIndex[j+1],l]	<- CostMatrix[RowIndex[j],k]+NodeDistMatrix[CurrentNode,NextNode]
										PreviousCol[RowIndex[j+1],l]	<- k
										TIPLOCMapped[RowIndex[j]]	<-TRUE
										TIPLOCMapped[RowIndex[j+1]]	<-TRUE
									}
								}
							}
						}
					}
				} else {
					CostMatrix[RowIndex[j+1],]	<- ZeroRow
					PathBreak[RowIndex[j]]		<- 1
				}				
			}
			if(min(CostMatrix[RowIndex[j+1],]) == Inf){CostMatrix[RowIndex[j+1],]	<- ZeroRow}
		}
#Construct Route
		j	<- length(RowIndex)
		LenPath	<- 0
		NumTIPLOCsMapped	<- 0
		repeat{
			while(all(is.na(PreviousCol[RowIndex[j],]))& j>0){
				j	<- j-1
			}
			if(j >1){
				Index	<- min(which(CostMatrix[RowIndex[j],] == min(CostMatrix[RowIndex[j],])))
				CurrentNodeCol	<- Index
				LenPath	<- LenPath+1
				NumTIPLOCsMapped	<- NumTIPLOCsMapped + 1
				TIPLOCsMapped[NumTIPLOCsMapped]
				Path[LenPath]	<- TIPLOCData[Timetable[RowIndex[j],8],CurrentNodeCol+3]
				repeat{
					NextNodeCol	<-	PreviousCol[RowIndex[j],CurrentNodeCol] 
					LenPath	<- LenPath+1
					Path[LenPath]	<- 	TIPLOCData[Timetable[RowIndex[j-1],8],NextNodeCol+3]
					if(is.na(PreviousCol[RowIndex[j-1],NextNodeCol])) break
					CurrentNodeCol	<- NextNodeCol
					j	<- j-1
				}
				LenPath	<- LenPath+1
				Path[LenPath]	<- DummyNodeId
			}
			j	<- j-1
			if(j < 1) break			
		}
		if(LenPath>0){
			LenPath2	<- 0
			for(j in 1:(LenPath-1)){
				if(Path[j+1] != Path[j] & Path[j+1]	!= DummyNodeId & Path[j]	!= DummyNodeId){
					CurNode	<- Path[j]
					repeat{
						LenPath2	<- LenPath2 + 1
						Path2[LenPath2]	<- CurNode
						CurNode	<- PreviousNode[Path[j+1],CurNode]
						if(CurNode == Path[j+1]) break
					}	
				}
				if(Path[j+1] == DummyNodeId){
					LenPath2	<- LenPath2 + 1
					Path2[LenPath2]	<- Path[j]
					LenPath2	<- LenPath2 + 1
					Path2[LenPath2]	<- DummyNodeId
				}			
			}
			ForwardPath	<- rev(Path2[1:(LenPath2-1)])
			TTSegments[NextTTStart:(NextTTStart+LenPath2-2)]	<- ForwardPath
			TTNum[NextTTStart:(NextTTStart+LenPath2-2)]	<- rep(i,LenPath2-1)
			TTHeadcode[NextTTStart:(NextTTStart+LenPath2-2)]	<- rep(Headcode,LenPath2-1)
			xx	<- NextTTStart
			NextTTStart	<- NextTTStart + LenPath2 -1
			TIPLOC	<- Timetable[StartTTIndex[i]:EndTTIndex[i],8][which(TIPLOCMapped[StartTTIndex[i]:EndTTIndex[i]]==TRUE)]
			# now remove consecutive repeated TIPLOCs
			if(length(which(diff(TIPLOC)==0))>0){
				TIPLOC	<- TIPLOC[-(which(diff(TIPLOC)==0)+1)]
				}
			k	<- 1
			CurrSegment		<- 0
			CurrDistance	<- 0
			CurrK			<- 0
			for(j in 1:length(TIPLOC)){
				TIPLOCFound	<- FALSE
				repeat{
					for(m in 1:TIPLOCData[TIPLOC[j],3]){
						if(TIPLOCData[TIPLOC[j],m+3]==ForwardPath[k]){
							if(ForwardPath[k] ==  CurrSegment){
								if(TIPLOC_File_Dist[TIPLOC[j],ForwardPath[k]] > CurrDistance | CurrK != k){
									TIPLOCFound = TRUE
									NumTIPOCsSegment[xx+k-1]	<- NumTIPOCsSegment[xx+k-1] +1
									TTMappedTIPLOCs[xx+k-1,NumTIPOCsSegment[xx+k-1]]	<- TIPLOCData[TIPLOC[j],2]
									CurrSegment	<- ForwardPath[k]
									CurrDistance	<- TIPLOC_File_Dist[TIPLOC[j],ForwardPath[k]]
									CurrK	<- k
								}
							} else {
								TIPLOCFound = TRUE
								NumTIPOCsSegment[xx+k-1]	<- NumTIPOCsSegment[xx+k-1] +1
								TTMappedTIPLOCs[xx+k-1,NumTIPOCsSegment[xx+k-1]]	<- TIPLOCData[TIPLOC[j],2]
								CurrSegment	<- ForwardPath[k]
								CurrDistance	<- TIPLOC_File_Dist[TIPLOC[j],ForwardPath[k]]
								CurrK	<- k
							}
						}
					}
					if(TIPLOCFound == TRUE) break 
					k	<- k+1
				}
			}
		}
	}
}

setwd(MainDir)
write.table(data.frame(TTNum[1:(NextTTStart-1)],TTHeadcode[1:(NextTTStart-1)],SegmentData[TTSegments[1:(NextTTStart-1)],2],NumTIPOCsSegment[1:(NextTTStart-1)],TTMappedTIPLOCs[1:(NextTTStart-1),]),"TTRoutes.txt",sep="\t",row.names=FALSE,col.names=FALSE,quote=FALSE)
Timetable[,9]	<- TIPLOCMapped
write.table(Timetable,"Timetable_TIPLOCs.txt",sep="\t",row.names=FALSE,col.names=FALSE,quote=FALSE)




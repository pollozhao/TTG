#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Freightliner/Timetables"
#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/Arriva XC/Timetables"
#MainDir		<- "C:/Users/scottm/Documents/Projects/UK/NIR/Timetable Mapping"
MainDir		<- "C:/Users/scottm/Documents/Projects/UK/ATW/Timetable Mapping"
#**********************************************************************

setwd(MainDir)
Mappings_df	<- read.table("SegmentMappings_R.txt",strip.white=TRUE,header=FALSE,quote="\"",as.is=T,fill=T,sep="\t",comment="#")
Mappings_df<- Mappings_df[Mappings_df[,1] != "" & Mappings_df[,2] != "",]
setwd(paste(MainDir,"/","Mapping Data",sep=""))
Segments	<- read.table("Segments.txt",strip.white=TRUE,header=TRUE,quote="\"",as.is=T,fill=T,sep="\t",comment="#")
numSegments	<- nrow(Segments)

Mappings_df <- unique(Mappings_df)
maxNumConnections	<- max(table(Mappings_df[,1]))
# Convert the Segment "From"  and "To" to a segment id number
SegId_From	<- match(Mappings_df[,1],Segments[,2])
SegId_To	<- match(Mappings_df[,2],Segments[,2])

# List the segments "From" that are not in the data
SegmentsFrom_NF	<- Mappings_df[which(is.na(SegId_From)==TRUE),1]
SegmentsTo_NF	<- Mappings_df[which(is.na(SegId_To)==TRUE),2]

for(i in SegmentsFrom_NF){cat("Segments from not found: ",i,"\n")}
for(i in SegmentsTo_NF){cat("Segments to not found: ",i,"\n")}

numSegmentConnections	<- rep(0,numSegments)
ConnectionsMatrix		<- matrix(data=NA,nrow=numSegments,ncol=maxNumConnections)
if(length(SegmentsFrom_NF) == 0 & length(SegmentsTo_NF) == 0){
	for(i in 1:numSegments){
		Connections <- SegId_To[SegId_From == i]
		if(length(Connections) > 0){
			numSegmentConnections[i] <- length(Connections)
			ConnectionsMatrix[i,1:length(Connections)]=Connections
		}
	}
}
DistMatrix			<- matrix(data=NA,nrow=numSegments,ncol=numSegments)
PreviousNodeMatrix	<- matrix(data=NA,nrow=numSegments,ncol=numSegments)

# Now use Dijkstra to calculate shortest path from each segment to every other segment
for(i in 1:numSegments){
	Distance	<- rep(Inf,numSegments)
	Previous	<- rep(NA,numSegments)

	# Source distance is 0
	Distance[i]	<- 0

	Break	<- FALSE

	# Q is the set of all nodes
	Q	<- !logical(numSegments)
	k=0
	while(any(Q == TRUE) & Break == FALSE){
		minDist	<- min(Distance[Q == TRUE])
		u	<- min(which(Distance == minDist & Q == TRUE))
		Q[u]	<- FALSE
		if(minDist == Inf){
			Break <- TRUE
		} else {
			if(numSegmentConnections[u] > 0){
				alt	<- Distance[u] + Segments[u,3]
				for(j in 1:numSegmentConnections[u]){
					if(alt < Distance[ConnectionsMatrix[u,j]]){
						Distance[ConnectionsMatrix[u,j]]	<- alt
						Previous[ConnectionsMatrix[u,j]]	<- u
					}
				}
			}
		}
	}
	DistMatrix[i,]		<- Distance
	PreviousNodeMatrix[i,]	<- Previous
}

write.table(DistMatrix,file="DistMatrix.txt",sep="\t",row.names=FALSE,quote=FALSE,col.names=FALSE)
write.table(PreviousNodeMatrix,file="ShortestPreviousNode.txt",sep="\t",row.names=FALSE,quote=FALSE,col.names=FALSE)

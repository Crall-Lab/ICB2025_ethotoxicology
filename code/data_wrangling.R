rm(list = ls())

# Load necessary libraries
library(tidyr)
library(lubridate)
library(zoo)
library(dplyr)
library(data.table)
library(stringr)

###### nest data

# Function to process each buzz analysis output
process_buzz_csv <- function(file_path) {
  data <- read.csv(file_path)

  # Combine date and time columns into a single datetime column
  data$datetime <- ymd_hms(paste(data$Date, data$Time), tz = "America/Chicago")
  # Sort the data by date and time
  data <- data %>% arrange(datetime)
  
  start_time <- min(data$datetime)
  end_time <- max(data$datetime)
  
  data$deployed_at <- start_time
  data$total_deployment_time <- as.numeric(difftime(end_time, start_time, units = "hours"))
  
  data <- data %>% mutate(time_since_deployment = as.numeric(difftime(datetime, start_time, units = "hours")))
  
  return(data)
}

# List all CSV files in the directory
setwd("/Users/anupreksha/Desktop/anupreksha/hoophouse2023/data/BuzzAnalyses")
file_list <- list.files(pattern = "*interpolated.csv")

# Process each file and combine the results
combined_data <- do.call(rbind, lapply(file_list, process_buzz_csv)) %>%
  mutate(datetime = floor_date(datetime, "minute"))

#read in tag data
tag_data <- read.csv('/Users/anupreksha/Desktop/anupreksha/hoophouse2023/data/tag_metadata.csv')
tag_data$start_date <- parse_date_time(tag_data$start_date, "m/d/y")
tag_data$end_date <- parse_date_time(tag_data$end_date, "m/d/y")
tag_data$microcolony <- paste(tag_data$round, tag_data$treatment, sep = "_")

#add trt and round using date and taglist
combined_data$treatment <- NA
combined_data$round <- NA
for(zz in 1:nrow(tag_data)){
  taglist <- seq(tag_data$tag_start[zz], tag_data$tag_end[zz])
  condition <- combined_data$bee_ID %in% taglist & combined_data$Date %in% c(tag_data$start_date[zz], tag_data$end_date[zz])
  combined_data$round[condition]  <- tag_data$round[zz]
  combined_data$treatment[condition] <- tag_data$treatment[zz]
}

combined_data$treatment <- as.factor(combined_data$treatment)
combined_data$round <- as.factor(combined_data$round)
combined_data$bee_ID <- as.factor(combined_data$bee_ID)

#Add microcolony by combining trt and round
combined_data$microcolony <- paste(combined_data$round, combined_data$treatment, sep = "_")

#filter to remove tags not used in the study (NA treatment/false reads)
combined_data <- subset(combined_data, !is.na(treatment))
combined_data <- subset(combined_data, bee_ID !=17)

#remove low track count bees and anomalous speed data (flying?)
combined_data = subset(combined_data, trackedFrames > 5 & (meanSpeed < 1000| is.na(meanSpeed)) ) 

# filter out low bee count videos
bee_counts <- combined_data %>% group_by(datetime) %>% summarise(bees_per_vid = n())
combined_data <- combined_data %>% left_join(bee_counts, by = "datetime") %>% filter(bees_per_vid > 3)

#remove bees found in wrong nests
table(combined_data$microcolony, combined_data$deployed_at)
combined_data <- subset(combined_data, 
                        !(deployed_at == '2023-08-01 17:45:01' & microcolony == '1_control') &
                          !(deployed_at == '2023-07-31 17:05:19' & microcolony == '1_imidacloprid') &
                          !(deployed_at == '2023-09-02 17:10:48' & microcolony == '5_imidacloprid') &
                          !(deployed_at == '2023-09-16 17:10:01' & microcolony == '8_flupyradifurone') &
                          !(deployed_at == '2023-08-17 16:25:01' & microcolony == '3_imidacloprid'))

file_list_nb <- list.files(pattern = "*nobrood.csv")
nb_data <- do.call(rbind, lapply(file_list_nb, process_buzz_csv)) %>%
  mutate(datetime = floor_date(datetime, "minute"))
missing_cols <- setdiff(names(combined_data), names(nb_data))
nb_data[missing_cols] <- NA
nb_data$microcolony <- "9_control"

missing_microcol <- data.frame(microcolony = "4_imidacloprid", deployed_at = as.POSIXct("2023-08-26 18:49:28", total_deployment_time = as.numeric("19.6")))
missing_cols <- setdiff(names(combined_data), names(missing_microcol))
missing_microcol[missing_cols] <- NA

combined_data <- rbind(combined_data, nb_data, missing_microcol)

# add sunset and sunrise times for each trial
# originally from https://www.timeanddate.com/sun/@5244160?month=9&year=2023
tag_data <- tag_data %>%
  mutate(sunset = ymd_hms(paste(start_date, sunset), tz = "America/Chicago"),
         sunrise = ymd_hms(paste(end_date, sunrise), tz = "America/Chicago"))
combined_data$sunrise <- NA
combined_data$sunset <- NA
for(zz in 1:nrow(tag_data)){
  combined_data$sunrise[combined_data$microcolony == tag_data$microcolony[zz]] <- tag_data$sunrise[zz]
  combined_data$sunset[combined_data$microcolony == tag_data$microcolony[zz]] <- tag_data$sunset[zz]
  combined_data$sunrise[combined_data$microcolony == tag_data$microcolony[zz]] <- tag_data$sunrise[zz]
  combined_data$sunset[combined_data$microcolony == tag_data$microcolony[zz]] <- tag_data$sunset[zz]
}
combined_data$sunrise <- as.POSIXct(combined_data$sunrise, tz = "America/Chicago")
combined_data$sunset <- as.POSIXct(combined_data$sunset, tz = "America/Chicago")

# classify day or night
combined_data <- combined_data %>%
  mutate(day_or_night = ifelse(datetime >= sunrise | datetime <= sunset, "day", "night"))

#Add interaction rate variable
combined_data$interaction.rate <- combined_data$totalInt/combined_data$totalIntFrames

combined_data <- combined_data %>% dplyr::ungroup() %>%
  dplyr::select(-pi_ID, -LR, -meanEggDistM, -meanLarvaeDistM, -PropLarvaeTime, -PropPupaeTime, -meanPupaeDistM)

# Write the combined data to a new CSV file
#write.csv(combined_data, "combinedIntBuzzAnalysis.csv", row.names = FALSE)


########## forage tunnel
setwd('..')
ft_data <- read.csv('forage_tunnel_detections.csv')

#Add numeric timestamp
#Set a common reference time
start.date <- parse_date_time('2023-07-31 00:00:00', "%Y-%m-%d %H:%M:%S", tz = "America/Chicago")
ft_data$timestamp <- as.POSIXct(ft_data$timestamp)
ft_data$date <- as.Date(ft_data$timestamp)
ft_data$time.num <- as.numeric(difftime(ft_data$timestamp, start.date, units = 'days'))

#add trt and round
tag_data <- read.csv('tag_metadata.csv')
tag_data$start_date <- parse_date_time(tag_data$start_date, "m/d/y")
tag_data$end_date <- parse_date_time(tag_data$end_date, "m/d/y")
for(zz in 1:nrow(tag_data)){
  taglist <- seq(tag_data$tag_start[zz], tag_data$tag_end[zz])
  condition <- ft_data$tag_id %in% taglist & ft_data$date %in% c(tag_data$start_date[zz], tag_data$end_date[zz])
  ft_data$round[condition]  <- tag_data$round[zz]
  ft_data$treatment[condition] <- tag_data$treatment[zz]
}
ft_data$treatment <- as.factor(ft_data$treatment)
ft_data$round <- as.factor(ft_data$round)
ft_data$microcolony <- paste(ft_data$round, ft_data$treatment, sep = "_")

#filter out false reads
ft_data <- subset(ft_data, tag_id !=17)
ft_data <- subset(ft_data, !is.na(ft_data$round))

#day or night
ft_data$sunrise <- setNames(combined_data$sunrise, combined_data$microcolony)[ft_data$microcolony]
ft_data$sunrise <- as.POSIXct(ft_data$sunrise, format="%Y-%m-%d %H:%M:%S", tz = "America/Chicago")
ft_data$sunset <- setNames(combined_data$sunset, combined_data$microcolony)[ft_data$microcolony]
ft_data$sunset <- as.POSIXct(ft_data$sunset, format="%Y-%m-%d %H:%M:%S", tz = "America/Chicago")
ft_data <- ft_data %>%
  mutate(day_or_night = ifelse(timestamp >= sunrise | timestamp <= sunset, "day", "night"))

ft_data$deployed_at <- setNames(combined_data$deployed_at, combined_data$microcolony)[ft_data$microcolony]
ft_data$deployed_at <- as.POSIXct(ft_data$deployed_at, format="%Y-%m-%d %H:%M:%S", tz = "America/Chicago")

#Create list of unique bees
bees <- unique(ft_data$tag_id)

#Define time interval for parsing unique bouts
time_interval <- 2/(60*24)

#Define function for estimating mean change in X for a bout 
#(bee going in or out)
direction_function <- function(x){
  delta <- mean(diff(x))
  return(delta)
}

#Start looping across bees to convert data into bouts
rm('comb_data') #Make sure output variable is clear
for(j in 1:length(bees)){
  
  #Subset to individual bee
  current.bee <- bees[j]
  bee_sub <- subset(ft_data, tag_id == current.bee)
  
  #Reorder by timestamp
  bee_sub <- bee_sub[order(bee_sub$time.num),]
  
  #Create cluster
  if(dim(bee_sub)[1] > 1){
    clusts <- hclust(dist(bee_sub$time.num))
    #generate separate bouts
    bee_sub$bout.ID <- as.factor(cutree(clusts, h = time_interval))
    
    #Get average change in direction for each bout and collect aggregate data for each bout
    ag_data <- aggregate(x~bout.ID, data = bee_sub, FUN = direction_function)
    ag_data_time <- aggregate(time.num~bout.ID, data = bee_sub, FUN = mean)
    ag_data$time.num <- ag_data_time$time.num
    ag_data$direction <- sign(ag_data$x)
    ag_data$bee_ID <- current.bee
    ag_data$round <- unique(bee_sub$round)
    ag_data$treatment <- unique(bee_sub$treatment)
    ag_data$microcolony <- unique(bee_sub$microcolony)
    ag_data$datetime <- start.date + as.difftime(ag_data$time.num, units = "days")
    ag_data$deployed_at <-  unique(bee_sub$deployed_at)

    # Calculate the frequency of each value in bee_sub$day_or_night
    freq_table <- table(bee_sub$day_or_night)
    # Determine the most frequent value
    most_frequent_value <- names(which.max(freq_table))
    # Assign the most frequent value to ag_data$day_or_night
    ag_data$day_or_night <- rep(most_frequent_value, nrow(ag_data))

    #Write into output data frame
    if(!exists('comb_data')){
      comb_data <- ag_data
    } else{
      comb_data <- rbind(comb_data, ag_data)
    }
  }
}
table(comb_data$direction, useNA = "ifany")

comb_data$total_deployment_time <- setNames(combined_data$total_deployment_time, combined_data$microcolony)[comb_data$microcolony]

# write.csv(comb_data, "forage_tunnel_bouts.csv", row.names = FALSE)

############# floral visitation

#Read in flower visitation data
lst <- list.files(pattern = "*FlowerTags.csv", recursive = TRUE)
rm(list = 'flower_data')
for(file in lst){
  fl_dat <-read.csv(file)
  if(!exists('flower_data')){
    flower_data <- fl_dat
  } else {
    flower_data <- rbind(flower_data, fl_dat)
  }
}

#pi clock issues in this round
flower_data <- flower_data[!grepl("sep10to13", flower_data$Video), ]

#Remove end brackets on tag data
flower_data$Tag.IDs <- str_sub(flower_data$Tag.IDs, 2, -2)

#Subset to data where some tags were detected
flower_data <- subset(flower_data, !(Tag.IDs == ""))

#enter datetime and camera from filename
flower_data$Date <- basename(dirname(flower_data$Video))
flower_data$Time <- basename(flower_data$Video)
clean_time_func <- function(time_string) {
  # Extract the first part (HHMMSS)
  time_part <- sub("_.*", "", time_string)
  # Extract the third part (camera identifier) and remove .mp4 extension
  camera_part <- sub(".*_", "", time_string)
  camera_part <- sub("\\.mp4$", "", camera_part)
  return(list(time_part = time_part, camera_part = camera_part))
}
cleaned_times <- lapply(flower_data$Time, clean_time_func)
flower_data$Time <- sapply(cleaned_times, function(x) x$time_part)
flower_data$Camera <- sapply(cleaned_times, function(x) x$camera_part)
flower_data$datetime <- paste(flower_data$Date, flower_data$Time)
flower_data$datetime <- strptime(flower_data$datetime, format = "%y%m%d %H%M%S")

#Loop over videos and count tags by trials
rm('out_data')
for(i in 1:length(flower_data[,1])){
  tags <- as.data.frame(table(unlist(strsplit(gsub(" ", "",flower_data$Tag.IDs[i]), ','))))
  colnames(tags) <- c("ID", "count")
  tags$camera <- flower_data$Camera[i]
  tags$datetime <- flower_data$datetime[i]
  if(!exists('out_data')){
    out_data <- tags
  } else{
    out_data <- rbind(out_data, tags)
  }
}

#Add treatment and round in to data frame
out_data$date <- as.Date(out_data$datetime)
for(zz in 1:nrow(tag_data)){
  taglist <- seq(tag_data$tag_start[zz], tag_data$tag_end[zz])
  condition <- out_data$ID %in% taglist & out_data$date %in% c(tag_data$start_date[zz], tag_data$end_date[zz])
  out_data$round[condition]  <- tag_data$round[zz]
  out_data$treatment[condition] <- tag_data$treatment[zz]
}
out_data$treatment <- as.factor(out_data$treatment)
out_data$round <- as.factor(out_data$round)

out_data <- subset(out_data, !is.na(out_data$round))
out_data <- subset(out_data, ID != 17)
out_data <- subset(out_data, round != 7)

#Write flower species data into out_data
cam_metadata <- read.csv('flowersp_metadata.csv')
for(i in 1:nrow(cam_metadata)){
  condition <- (out_data$camera == cam_metadata$camera[i]) & (out_data$round == cam_metadata$round[i])
  out_data$species[condition]  <- cam_metadata$species[i]
}

#count = 1 could be false positives, check
c1 <- out_data[out_data$count == 1, ]
c1_sample <- c1[sample(nrow(c1), size = 5), ]
#manually viewed videos, 4/5 were false positives
out_data <- subset(out_data, count >1)

out_data$microcolony <- paste(out_data$round, out_data$treatment, sep = "_")

#write.csv(out_data, "flower_visits.csv")
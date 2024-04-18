clear all;
%% read BFM data
folderPath = '.\BFM_data\'; 
files = dir(folderPath);
files = files(~[files.isdir]); 
fileNames = {files.name};
fileNumbers = zeros(1, length(fileNames));
for i = 1:length(fileNames)
    fileName = fileNames{i};
    fileNumbers(i) = str2double(fileName(end-9:end-4));
end
[~, sortedIndices] = sort(fileNumbers);
concatenatedData = [];
concatenatedMAC =[];
timestamp = [];
for i = 1:length(sortedIndices)
    sortedFileName = fileNames{sortedIndices(i)};
    filePath = fullfile(folderPath, sortedFileName);
    disp(['Processing file: ', filePath]);
    data = load(filePath);
    
    
    if isempty(concatenatedData)
        concatenatedData = data.packet_infos; 
        concatenatedMAC = data.ether_srcs;
        timestamp = str2num(data.packet_timestamps);
    else
        time=str2num(data.packet_timestamps);
        concatenatedData = cat(1, concatenatedData, data.packet_infos);
        concatenatedMAC =cat(1,concatenatedMAC,data.ether_srcs);
        timestamp = cat(1,timestamp,time);
    end
       
end
 
mac_addr_list=unique(concatenatedMAC,'row');
mac_addr = cellstr(concatenatedMAC);
mac_datasize = [];
for k = 1:size(mac_addr_list,1)
    idx=find(strcmp(mac_addr, mac_addr_list(k,:)));
    mac_datasize = [mac_datasize, length(idx)];
end
[~,max_id] = max(mac_datasize);
idx = find(strcmp(mac_addr, mac_addr_list(max_id,:)));
concatenatedData = concatenatedData(idx,:,:,:);
timestamp = timestamp(idx);

%% BFM  ratio
Ant_idx = [2,1]; % Two elements for BFM ratio
BFM_ratio = squeeze(concatenatedData(:,Ant_idx(1),1,:)./concatenatedData(:,Ant_idx(2),1,:));
figure
subplot(211)
plot(timestamp,abs(BFM_ratio))
xlabel('time')
ylabel('amplitude of BFM ratio')
subplot(212)
plot(timestamp,unwrap(angle(BFM_ratio)))
xlabel('time')
ylabel('phase of BFM ratio')







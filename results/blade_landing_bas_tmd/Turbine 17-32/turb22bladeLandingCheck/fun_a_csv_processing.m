function fun_a_csv_processing(CSVFullFileNames,accelOutputFullFileName,accelCellsOutputFullFileName,positionOutputFullFileName)
		
		  
% 		  N:\NextCloud\data\turbines\turbine-21\helihoist-1\tom\clean
% 		CSVInputFolder				= @(SensorName,TurbineNr) "N:\NextCloud\data\turbines\turbine-"+num2str(TurbineNr,"%02d")+"\"+SensorName+"\tom\clean\";
% 		OutputTurbineFolder		= @(TurbineNr) "N:\MAT-Files\Responses\turbine-"+num2str(TurbineNr,"%02d")+"\";
% 		OutputFullFileName		= @(SensorName,State,Type,TurbineNr) OutputTurbineFolder(TurbineNr)+SensorName+"_"+Type+"_"+State+".mat";
% 		
% 		f = waitbar(0,'1','Name','Process raw turbine data...','CreateCancelBtn','setappdata(gcbf,''canceling'',1)');setappdata(f,'canceling',0);	progrsturb	= 0;
		
% 		t_start = clock;
		
% 		aprroxready = "...";
		
% 		ncsvcompleted = 0;
% 		nsenscompleted = 0;
		
		% 	totexpected_sensors = length(TurbineNumbers)*length(NewNames);
		% 	totexpectedcsv =
		
% 		for TurbineNr = TurbineNumbers
				
% 				nested_function;
				
% 		end
		
% 		delete(f)
		
		
		
		
		
% 		function nested_function
				
				
% 				fid = fopen(logfile, 'a');
% 				fprintf(fid,'\r\nStarted processing raw acceleration and position data at: %s',datestr(datetime('now'),'HH:MM:SS'));fprintf(fid,'\r\nSensor:  ');
% 				fclose(fid);
% 				
% 				fid = fopen(overlapcsvlog, 'a');
% 				fprintf(fid,'\r\nStarted processing raw acceleration and position data at: %s\r\n',datestr(datetime('now'),'HH:MM:SS'));
% 				fclose(fid);
				
				
				
% 				fprintf('\nStarted processing raw acceleration and position data at: %s',datestr(datetime('now'),'HH:MM:SS'));fprintf('\nSensor:  ');
% 				t1 = clock;
				
% 				if(~exist(OutputTurbineFolder(TurbineNr),'dir'))
% 						mkdir(OutputTurbineFolder(TurbineNr));
% 				end
				
% 				csvfilenamesOverlapping = string.empty(0,2);
				
% 				nerr = 0;%zeros(length(OriginalNames),1);
				
% 				for isens = 1:numel(OriginalNames)
						
% 						ncsvcompleted =  ncsvcompleted+1;
						
% 						fid = fopen(logfile, 'a');
% 						fprintf(fid,'%s',NewNames(isens));
% 						fclose(fid);
% 						fprintf('%s',NewNames(isens));
% 						
% 						if(isens<numel(OriginalNames))
% 								fid = fopen(logfile, 'a');
% 								fprintf(fid,',  ');
% 								fclose(fid);
% 								fprintf(',  ');
% 						end
						
						
% 						if(getappdata(f,'canceling'));set(groot,'ShowHiddenHandles','on');
% 								delete(get(groot,'Children'));
% 								return
% 						end
						
						
% 						progrssfract = progrsturb/length(TurbineNumbers)+1/length(TurbineNumbers)*(isens-1)/numel(OriginalNames);
% 						waitbar(progrssfract,f,sprintf('%2.1f%%, completed at: %s',progrssfract*100,aprroxready));
% 						
						
% 						OrigName		= OriginalNames(isens);
% 						if(~isfolder(CSVInputFolder(OrigName,TurbineNr)))
% 								continue
% 						end
% 						
% 						CSVFileList			= sort(string(ls((CSVInputFolder(OrigName,TurbineNr)+"*.CSV"))));
% 						if(strcmp(CSVFileList,""))
% 								continue
% 						end
% 						CSVFullFileNames	= CSVInputFolder(OrigName,TurbineNr)+CSVFileList;
						
						
% 						clear csvfilenames time_endpoints epoch Traw_data
						
						
						Traw_data = table.empty(0,7);
						Traw_data.Properties.VariableNames = ["epoch","acc_x", "acc_y", "acc_z", "latitude", "longitude", "elevation"];
						
						
						
						
						n = 1;
						
						
						icsv = 0;
						
% 						epochcsvindx = [];
						
						
						if ischar(CSVFullFileNames)
								  CSVFullFileNames = string(CSVFullFileNames);
						end
						
						
						for csvfile = CSVFullFileNames(:)'
								  
								  		icsv = icsv+1;
								
% 								progrssfract = progrsturb/length(TurbineNumbers)+1/length(TurbineNumbers)*(isens-1)/numel(OriginalNames)+1/length(TurbineNumbers)*1/numel(OriginalNames)*n/(length(CSVFullFileNames));
% 								waitbar(progrssfract,f,sprintf('%12.1f%%, \t completed at: %s',progrssfract*100,aprroxready));
% 								if(getappdata(f,'canceling'));set(groot,'ShowHiddenHandles','on');delete(get(groot,'Children'));return;end
								

								
								filedirinf=dir(csvfile);
								if filedirinf.bytes<= 100
% 										fid = fopen(logfile,'a');
% 										fprintf(fid,"\r\n\tWARNING: File '%s' is empty, and thus skipped",csvfile);
% 										fclose(fid);
										fprintf("\n\tWARNING: File '%s' is empty, and thus skipped",csvfile);
										continue
								end
								
												
								TCSVraw_data = [];
								opts = detectImportOptions(csvfile);
								opts.SelectedVariableNames = ["epoch","acc_x", "acc_y", "acc_z", "latitude", "longitude", "elevation"];
								TCSVraw_data = readtable(csvfile,opts);
								
								
								
								if(isempty(TCSVraw_data))
% 										fid = fopen(logfile,'a');
% 										fprintf(fid,"\r\nWARNING: File '%s' is empty, and thus skipped",csvfile);
% 										fclose(fid);
										fprintf("\nWARNING: File '%s' is empty, and thus skipped",csvfile);
										continue
								end
								
								
								
								if ~any(TCSVraw_data.acc_x) || ~any(TCSVraw_data.acc_y) || ~any(TCSVraw_data.acc_z)
										warning("\tWARNING: Accelerations in file '%s; are zero in one or more directions, file is skipped",csvfile)
% 										fid = fopen(logfile,'a');
% 										fprintf(fid,"\r\nFile '%s' is empty, and thus skipped",csvfile);
% 										fclose(fid);
										fprintf("\nFile '%s' is empty, and thus skipped",csvfile);
										continue
								end
								
								assert(issorted(TCSVraw_data.epoch),"Epoch time stamps are not sorted in ascending order, see file '%s'",csvfile)
								
								
								if n>1 && max(Traw_data.epoch(:))>min(TCSVraw_data.epoch(:))
% 										nerr = nerr+1;
% 									fid = fopen(overlapcsvlog, 'a');
% 										fprintf(fid,"\r\n Overlapping csv file timestamps: \r\n\t%s\r\n\t%s",CSVFullFileNames(icsv-1),CSVFullFileNames(icsv));
% 										fclose(fid);
									fprintf("\n Overlapping csv file timestamps: \n\t\t%s\n\t\t%s",CSVFullFileNames(icsv-1),CSVFullFileNames(icsv));										
								end
								
								Traw_data = [Traw_data;TCSVraw_data];
								
								
								
								if(isempty(Traw_data));continue;end
% 								
% 								epochcsvindx			= [epochcsvindx;icsv*ones(length(TCSVraw_data.epoch),1)];
% 								csvfilenames(n,1)		= csvfile;
% 								time_endpoints(n,1)	= TCSVraw_data.epoch(1);
% 								time_endpoints(n,2)	= TCSVraw_data.epoch(end);
								
							
								
								acceleration_cells{n,1}	= [TCSVraw_data.acc_x(:),TCSVraw_data.acc_y(:),TCSVraw_data.acc_z(:)];
								epoch_cells{n,1}				= TCSVraw_data.epoch;
								
								n=n+1;
								
								TCSVraw_data = [];
						
						end
						
						
						
		
						
% 						totdur = etime(clock,t_start);
% 						mintpercsv = totdur/ncsvcompleted;
% 						rem_time = (totexpectedcsv - ncsvcompleted)*mintpercsv;
% 						
						
						
% 						
% 						
% 						if any(nerr>0)
% 								for ierrsens = find(nerr>0)
% 										fid = fopen(logfile, 'a');
% 										fprintf(fid,"\r\n Number of CSV time overlap of turbine nr. %d, sensor %s: %d",TurbineNr,OriginalNames(ierrsens),nerr(ierrsens));
% 										fclose(fid);
% 										fprintf("\n Number of CSV time overlap turbine %d, sensor %s: %d",TurbineNr,OriginalNames(ierrsens),nerr(ierrsens));
% 								end
% 						end
						
						
						% 			assert(issorted(Traw_data.epoch),"Epoch time stamps ofturbine %d, sensors %s are not sorted",TurbineNr,OrigName)
						
						
% 						EPI = sortrows([Traw_data.epoch,epochcsvindx],1);
% 						epochcsvindx = EPI(:,2);
						
% 						Traw_data = sortrows(Traw_data,'epoch');
						
						
						assert(issorted(Traw_data.epoch),"Epoch time stamps are not sorted")
						
						
						
						
						epoch				= Traw_data.epoch;
						latitude			= Traw_data.latitude;
						longitude		= Traw_data.longitude;
						elevation		= Traw_data.elevation;
						acceleration	= [Traw_data.acc_x(:),Traw_data.acc_y(:),Traw_data.acc_z(:)];
						
						
% 						NewName		= NewNames(isens);
						
						
						save(accelOutputFullFileName,'epoch','acceleration');
						
						save(positionOutputFullFileName,'epoch','latitude','longitude','elevation');
						
						
						epoch = epoch_cells;
						acceleration = acceleration_cells;
						save(accelCellsOutputFullFileName,'epoch','acceleration');
						
						
						
% 						save(OutputFullFileName(NewName,"raw","timestamps",TurbineNr),'epoch','csvfilenames','time_endpoints','epochcsvindx');
						
% 						nsenscompleted = nsenscompleted+1;
						
						
% 				end
% 		%%		
% 				
% 				
% 								
% 						
% 						if any(nerr>0)
% 								  fprintf("\n")
% 								  fid = fopen(logfile, 'a');
% 								  fprintf(fid,"\r\n");
% 								  fclose(fid);
% 								for ierrsens = find(nerr>0)
% 										fid = fopen(logfile, 'a');
% 										fprintf(fid,"\r\n Number of CSV time overlap of turbine nr. %d, sensor %s: %d",TurbineNr,OriginalNames(ierrsens),nerr(ierrsens));
% 										fclose(fid);
% 										fprintf("\n Number of CSV time overlap turbine %d, sensor %s: %d",TurbineNr,OriginalNames(ierrsens),nerr(ierrsens));										
% 								end
% 								fprintf("\n")
% 						end
				
				
				
				
% 				t2 = clock;dur = etime(t2,t1);
% 				fid = fopen(logfile, 'a');
% 				fprintf(fid,'\r\n completed processing raw acceleration and position data at: %s ',TurbineNr,datestr(datetime('now'),'HH:MM:SS'));
% 				fprintf(fid,'\t\t(elapsed time: %s)',datestr(seconds(dur),'HH:MM:SS'));
% 				fclose(fid);
% 				fprintf('\n completed processing raw acceleration and position data at: %s ',TurbineNr,datestr(datetime('now'),'HH:MM:SS'));
% 				fprintf('\n(elapsed time: %s\n)',datestr(seconds(dur),'HH:MM:SS'));
% 				
% 				progrsturb = progrsturb+1;
% 				
% 				aprroxready = string(datestr(seconds(etime(clock,t_start)/progrsturb*(length(TurbineNumbers)-progrsturb))+datetime('now'),"HH:MM:SS"));
% 				
				%
				% 		avrcsvpersens = ncsvcompleted/(progrsturb*length(NewNames));
				% 		totexpectedcsv = avrcsvpersens*length(TurbineNumbers)*length(NewNames);
				
				
				
		end
% end

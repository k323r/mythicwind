function varargout = FileList(directory,varargin)
		
		  
		  
		
		  
		  
		if nargin > 1
				   
				  searchStr = strjoin(strip(strtrim(string(varargin)),"*"),"*");
					
				
				if ~endsWith(directory,"\")
						
						directory = directory+"\";
						
				end
				
				directory = directory+"*"+searchStr;
				
		end
		
				
				
		d = dir(directory);
		
		d = d(~ismember({d.name},{'.','..'}));
		
		filenames = string({d.name}');
		
		if nargout == 0
				
				disp(filenames)
				
		elseif nargout ==1
				
				varargout{1} =filenames;
		end
		
		
		
end


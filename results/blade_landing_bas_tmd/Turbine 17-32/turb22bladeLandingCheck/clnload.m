function varargout = clnload(FileName,varargin)
	
	
	
	
	data = load(FileName,varargin{:});
	
	fnames = string(fieldnames(data));
	
	
	if length(fnames) == 1
		
		varargout{1} = data.((fnames(:)));
		
		return
		
	end
	
	
	if nargout == nargin -1
		
		for jj=1:nargout
			
			varargout{jj} = data.(varargin{jj});
			
		end
		
	else
		
		varargout{1} = data;
	end
	
	
	
	
end


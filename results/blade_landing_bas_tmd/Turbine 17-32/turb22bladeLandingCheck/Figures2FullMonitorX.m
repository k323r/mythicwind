function Figures2FullMonitorX(varargin)
		  
		  if nargin == 1
					 Imon = varargin{1};
		  else
					 Imon=1;
		  end
		  
		  monpos = get(0,'MonitorPositions');
		  monPosSel = monpos(Imon,:);
		  
		  Wmon = monPosSel(3);
		  Hmon = monPosSel(4);
		  
		  
		  VmarginFac = 0;05;
		  HmarginFac = 0.02;
		  
		  
		  Hfigmargin = ceil(HmarginFac*Wmon);
		  Vfigmargin = ceil(VmarginFac*Hmon);
		  
		  Hfig = Hmon-2*Vfigmargin;
		  Wfig = Wmon -2*Hfigmargin;
		  
		  
		  
		  set(0,'DefaultFigurePosition', [monPosSel(1)+Hfigmargin, monPosSel(2)+Vfigmargin,Wfig,Hfig]);
end


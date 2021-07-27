clear;close all;clc;
% rmpath('D:\global functions\');
% Figures2FullMonitorX(2);


dataFolder	= @(Isens) fullfile(cd,"helihoist"+num2str(Isens));
searchStr	= @(Isens) "helihoist-"+num2str(Isens)+"*.csv";

csvFiles		= @(Isens) dataFolder(Isens)+"\"+FileList(dataFolder(Isens),searchStr(Isens));

outpFile_accel					= @(Isens) fullfile(dataFolder(Isens),"raw_accel_helhoist_"+num2str(Isens)+".mat");
outpFile_accel_cells			= @(Isens) fullfile(dataFolder(Isens),"raw_accel_cells_helhoist_"+num2str(Isens)+".mat");
outpFile_positions			= @(Isens) fullfile(dataFolder(Isens),"raw_position_helhoist_"+num2str(Isens)+".mat");


% csvFiles(sensNr)
% outpFile_accel(sensNr)
% outpFile_accel_cells(sensNr)
% outpFile_positions(sensNr)


for sensNr = 1:2
		  if exist(outpFile_accel(sensNr),'file')~=2
					 
		  fun_a_csv_processing(csvFiles(sensNr),outpFile_accel(sensNr),outpFile_accel_cells(sensNr),outpFile_positions(sensNr));
		  end
end


%%




[T1,A1] = clnload(outpFile_accel(1),'epoch','acceleration');


[T2,A2] = clnload(outpFile_accel(2),'epoch','acceleration');





%%
close all
clc;





t_start_perc	=  76;

plotdur_perc = .5;


dofnames = ["x","y","z"];



[I1,I2]=ismember(T1,T2);

t1_shrd = T1(I1);
a1_shrd = A1(I1,:);

t2_shrd = T2(I2(I2~=0));
a2_shrd = A2(I2(I2~=0),:);


ampdev = 100*(abs(a2_shrd(:,1)-a1_shrd(:,1))./prctile(abs([a1_shrd(:,1);a2_shrd(:,1)]),99.999));

figure
plot(t1_shrd,ampdev)


t_min_init = max([min(t1_shrd);min(t2_shrd)]);

t1_shrd = t1_shrd-t_min_init;
t2_shrd = t2_shrd-t_min_init;

t1_shrd = t1_shrd/60;
t2_shrd = t2_shrd/60;

t_min = max([min(t1_shrd);min(t2_shrd)]);
t_max = min([max(t1_shrd);max(t2_shrd)]);




dur	= t_max-t_min;

t_start = dur*t_start_perc/100;

t_end		= min(t_start+plotdur_perc/100*dur,t_max);






I1 = t1_shrd>t_start & t1_shrd<t_end;
I2 = t2_shrd>t_start & t2_shrd<t_end;

t1_shrd = t1_shrd(I1);
a1_shrd = a1_shrd(I1,:);


t2_shrd = t2_shrd(I2);
a2_shrd = a2_shrd(I2,:);




% a1 = a1.*abs(a1.^2);
% a2 = a2.*abs(a2.^2);






% [I1,I2]=ismember(T1,T2);

% t1 = T1(I1);
% a1 = A1(I1,:);
%
% t2 = T2(I2(I2~=0));
% a2 = A2(I2(I2~=0),:);


t1 = T1;
t2 = T2;
a1 = A1;
a2 = A2;



% t_min = max([min(t1);min(t2)]);

t1 = t1-t_min_init;
t2 = t2-t_min_init;

t1 = t1/60;
t2 = t2/60;

% t_min = max([min(t1);min(t2)]);
% t_max = min([max(t1);max(t2)]);
%
%
%
%
% dur	= t_max-t_min;
%
%
% t_start	=  6.8;
% t_end		= t_max;



I1 = t1>t_start & t1<t_end;
I2 = t2>t_start & t2<t_end;

t1 = t1(I1);
a1 = a1(I1,:);


t2 = t2(I2);
a2 = a2(I2,:);


normval = prctile(abs([a1;a2]),99.9);
a1 = a1./normval;
a2 = a2./normval;



% normval = prctile(abs(a1_shrd),99.9);
a1_shrd = a1_shrd./normval;
a2_shrd = a2_shrd./normval;


%
% for jj=(1:3)
%
% 		  figure('WindowState','maximized');
% 		  tiledlayout(3,1);
%
%
%
% 		  for ii = 1:3
%
% 					 nexttile
% 					 hold on
% 					 plot(t1,a1(:,jj),'b','LineWidth',0.8,'DisplayName',"sensr.1-"+dof(jj));
% 					 plot(t2,a2(:,ii),'r','LineWidth',0.8,'DisplayName',"sensr.2-"+dof(ii));
% 					 p3=plot(t1,a1(:,jj),'-.b','LineWidth',0.8);
% 					 set(p3,'tag','hline','handlevisibility','off')
% 					 p4=plot(t2,a2(:,jj),':r','LineWidth',0.6);
% 					 set(p4,'tag','hline','handlevisibility','off')
% 					 ylim([-1,1]);
% 					 xlim([t_start,t_end]);
% 					 legend('show');
% 		  end
%
% end





Ntiles = 6;

plot_dur = t_end-t_start;
tiledur = plot_dur/Ntiles;

tileLim1 = [0; cumsum(tiledur*ones(Ntiles-1,1))]+t_start;
tileLim2 = tileLim1+tiledur;

tileLimts = [tileLim1,tileLim2];



dofnr = 3;


figure('WindowState','maximized','color',[1 1 1]*.5);
tllo=tiledlayout(Ntiles,1);
tllo.Padding = 'none';
tllo.TileSpacing = 'none';
title(tllo,"Motion in "+dofnames(dofnr)+"-direction");


for ii = 1:Ntiles
		  
		  nexttile
		  hold on
		  plot(t1-t_start,a1(:,dofnr),'w','LineWidth',0.5,'DisplayName',"sensr.1-"+dofnames(dofnr));
		  plot(t2-t_start,a2(:,dofnr),'b','LineWidth',0.8,'DisplayName',"sensr.2-"+dofnames(dofnr));

% 		  scatter(t1_shrd-t_start,a1_shrd(:,dofnr),100,'r','DisplayName',"sensr.1- shared time stamp")
% 		  scatter(t2_shrd-t_start,a2_shrd(:,dofnr),100,'w','Marker','square','DisplayName',"sensr.2- shared time stamp")



				 ylim([-1,1]);
		  xlim(tileLimts(ii,:)-t_start);
% 		  legend('show');
		if ii == Ntiles
				  legend('show');
		end
		
		  ax = gca;
		  ax.Clipping = 'off';
% 		  ax.YAxisLocation = 'origin';
		  ax.XAxisLocation = 'origin';
		  ax.TickLength = [0.001,0.001];
		  ax.Visible = 'off';
end



fig = gcf;


export_fig(fig,fullfile(cd,"helihois1_helihoist2_raw_acceleration.png"),'-png')



















%
% for jj=(1:3)
%
% 		  figure('WindowState','maximized');
% 		  tiledlayout(3,1);
%
%
%
% 		  for ii = 1:3
%
% 					 nexttile
% 					 hold on
% 					 plot(t1_shrd,a1_shrd(:,jj),'b','LineWidth',0.8,'DisplayName',"sensr.1-"+dof(jj));
% 					 plot(t2_shrd,a2_shrd(:,ii),'r','LineWidth',0.8,'DisplayName',"sensr.2-"+dof(ii));
% 					 p3=plot(t1_shrd,a1_shrd(:,jj),'-.b','LineWidth',0.8);
% 					 set(p3,'tag','hline','handlevisibility','off')
% 					 p4=plot(t2_shrd,a2_shrd(:,jj),':r','LineWidth',0.6);
% 					 set(p4,'tag','hline','handlevisibility','off')
% 					 ylim([-1,1]);
% 					 xlim([t_start,t_end]);
% 					 legend('show');
% 		  end
%
% end


%%
%
%
%
% [I1,I2]=ismember(T1,T2);
%
% t1 = T1(I1);
% a1 = A1(I1,:);
%
% t2 = T2(I2(I2~=0));
% a2 = A2(I2(I2~=0),:);
%
%
%
%
%
%
% t_min = max([min(t1);min(t2)]);
%
% t1 = t1-t_min;
% t2 = t2-t_min;
%
% t1 = t1/3600;
% t2 = t2/3600;
%
% t_min = max([min(t1);min(t2)]);
% t_max = min([max(t1);max(t2)]);
%
%
%
%
% dur	= t_max-t_min;
%
%
% t_start	=  6.8;
% t_end		= t_max;
%
%
%
% I1 = t1>t_start & t1<t_end;
% I2 = t2>t_start & t2<t_end;
%
% t1 = t1(I1);
% a1 = a1(I1,:);
%
%
% t2 = t2(I2);
% a2 = a2(I2,:);
%
%
% normval = prctile(abs(a1),99.9);;
% a1 = a1./normval;
% a2 = a2./normval;

% a1 = a1.*abs(a1.^2);
% a2 = a2.*abs(a2.^2);


%
%
%
% for jj=(1:3)
%
% 		  figure('WindowState','maximized');
% 		  tiledlayout(3,1);
%
%
%
% 		  for ii = 1:3
%
% 					 nexttile
% 					 hold on
% 					 plot(t1,a1(:,jj),'b','LineWidth',0.8,'DisplayName',"sensr.1-"+dof(jj));
% 					 plot(t2,a2(:,ii),'r','LineWidth',0.8,'DisplayName',"sensr.2-"+dof(ii));
% 					 p3=plot(t1,a1(:,jj),'-.b','LineWidth',0.8);
% 					 set(p3,'tag','hline','handlevisibility','off')
% 					 p4=plot(t2,a2(:,jj),':r','LineWidth',0.6);
% 					 set(p4,'tag','hline','handlevisibility','off')
% 					 ylim([-1,1]);
% 					 xlim([t_start,t_end]);
% 					 legend('show');
% 		  end
%
% end
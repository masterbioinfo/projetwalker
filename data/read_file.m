
%%

function [del_res,shifts]=read_file(tresh)
%process a titration list in a sparky format and derive delta delta
%locate list files and separate list files from other files

f=dir('/data/olivier/recherche/Ub_E2_substrate_project/UIM-SH3/data_processing/titration_peptide_PP_070515/*.list');
cd /data/olivier/recherche/Ub_E2_substrate_project/UIM-SH3/data_processing/titration_peptide_PP_070515
tab_N=[];tab_H=[];

% Sort list files in ascending orders (don't forget to put '0' when list
% number is lesss than 10). For exemple: if the files are like this:
% hhh_1.list,hhh_2.list,hhh_12.list. Put hhh_01.list,hhh_02.list, etc
b=sort({f.name})'
fprintf('found %d list files for %d different concentrations\n\n',size(b,1),size(b,1));

nconc=size(b,1);
%Extract HN and N shifts for each list file
for ii=1:size(b,1)
    filename=b{ii};
    
    %remove the 'N-H' string from Sparky peak list
    system(sprintf('sed ''s/N-H//g'' %s > test.txt',filename));
    [res,N,H]=textread('test.txt','%d %f %f','headerlines',2);
  

    tab_N=[[tab_N],N];
    tab_H=[[tab_H],H];

end


cd /data/olivier/recherche/Matlab/titration






%%Calculate Deltadelta
N=[];HN=[];
for jj=1:nconc
    
    N(:,jj)=tab_N(:,jj)-tab_N(:,1);
    HN(:,jj)=tab_H(:,jj)-tab_H(:,1);
end


%[D]=SVD_ana(N,HN);

Delta=sqrt(HN.^2+(N./5).^2);
del_res=Delta;
shifts=[res,del_res];

[D]=SVD_ana_pond(del_res);


figure
for kk=1:nconc
    subplot(nconc,1,kk)
    bar(res(:,1),Delta(:,kk))
end




[nres,nshifts]=size(del_res);
%n_res_pface=fix(sqrt(nres))+1; %determine the length of the subplot



%Select only residues which have shifts higher than treshold
newHN=[];newN=[];
for ll=1:nres
    if shifts(ll,end)>=tresh
        newHN=[newHN;[res(ll,1),HN(ll,:)]];
        newN=[newN;[res(ll,1),N(ll,:)]];
    end    
end

n_res_pface=fix(sqrt(size(newHN,1)))+1
clr=jet(nshifts);



figure()
for jj=1:size(newHN,1)
    subplot(n_res_pface,n_res_pface,jj);
    box on;
    for kk=2:nshifts
        hold on
        h(kk)=plot(newHN(jj,kk),newN(jj,kk),'o','Color',clr(kk,:));
    end
    title(['res # ',num2str(newHN(jj,1))])
    axis([-0.3 0.3 -1.5 1.5]);
    set(gca,'XDir','reverse','YDir','reverse');
end
 
 [ax,h]=subtitle('CSPs directions from Blue to Red'); 
        




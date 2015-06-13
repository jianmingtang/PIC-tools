;
;    Copyright (C) 2014  Jian-Ming Tang <jmtang@mailaps.org>
;
;    This program is free software: you can redistribute it and/or modify
;    it under the terms of the GNU General Public License as published by
;    the Free Software Foundation, either version 3 of the License, or
;    (at your option) any later version.
;
;    This program is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;    GNU General Public License for more details.
;
;    You should have received a copy of the GNU General Public License
;    along with this program.  If not, see <http://www.gnu.org/licenses/>.
;


;+
;	This class is used to load EM fields from LANL PIC data
;-
pro FieldLANL__define
	compile_opt idl2
	data = { FieldLANL, xmax:0., zmax:0., nnx:0L, nnz:0L, $
		 path:'', nx:0L, nz:0L }
end

function FieldLANL::init, path
	self.path = path
	self.nx = 1000
	self.nz = 800
	return, 1
end

function FieldLANL::read_info, path
	; open binary file for problem description 
	if ( file_test(directory+'/info') eq 1 ) then begin
   		print," *** Found Data Information File *** "
	endif else begin
		print," *** Error - File info is missing ***"
	endelse
	openr, id, path+'/info',/f77_unformatted, /get_lun
	readu, id, nx,ny,nz
	readu, id, xmax,ymax,zmax
	close, id

	; Find the names of data files in the data directory

	datafiles = file_search(path+'/*.gda',count=numq)

	; Now open each file and save the basename to identify later

	print," Number of files=",numq
	plotme = strarr(numq+1)
	instring='     '
	plotme(0)='None'
;	for i=1,numq do begin
 ;   		if (not little) then openr,i,datafiles(i-1)
;		else openr,i,datafiles(i-1)
 ;   		plotme(i) = file_basename(datafiles(i-1),'.gda')
  ;  		print,"i=",i," --> ",plotme(i)
;	endfor

	return, 1
end


function FieldLANL::update, time
	return, self.field[time]
end

function FieldLANL::get, var, time
	fstruct = { data:fltarr(self.nx,self.nz),time:0.0,it:500000 }
	fname = self.path + '/' + var + '.gda'
	openr, id, fname, /f77_unformatted, /get_lun
	field = assoc(id, fstruct)
	res = fltarr(self.nx,self.nz)
	res = field[time]
	close, id
	return, res
end

pro FieldLANL::print
	print, format='("Field range: x=(",(F8.3),",",(F8.3),' $
		+ '"), z=(",(F8.3),",",(F8.3),")")', $
		(*self.xe)[0],(*self.xe)[-1],(*self.ze)[0],(*self.ze)[-1]
end

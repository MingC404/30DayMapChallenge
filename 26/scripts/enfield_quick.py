"""Run the final fixed screening parameters on Enfield Creek."""
import gorge_quick as quick
from enfield_trial import D,V
if __name__=='__main__':
 quick.D=D;quick.V=V;quick.SITE='Enfield Creek, Robert H. Treman';quick.SOURCE_LABEL='USGS 3DHP GA50N / 5SSOR / 9G3IV / 75EPE / CF25T / G2HV8; Enfield Creek only';quick.main()

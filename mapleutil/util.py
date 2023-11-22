exp_table = [15,34,57,92,135,372,560,840,1242,1242,1242,1242,1242,1242,1490,1788,2145,2574,3088,3705,4446,5335,6402,7682,9218,11061,13273,15927,19112,19112,19112,19112,19112,19112,22934,27520,33024,39628,47553,51357,55465,59902,64694,69869,75458,81494,88013,95054,102658,110870,119739,129318,139663,150836,162902,175934,190008,205208,221624,221624,221624,221624,221624,221624,238245,256113,275321,295970,318167,342029,367681,395257,424901,456768,488741,522952,559558,598727,640637,685481,733464,784806,839742,898523,961419,1028718,1100728,1177778,1260222,1342136,1429374,1522283,1621231,1726611,1838840,1958364,2085657,2221224,2365603,2365603,2365603,2365603,2365603,2365603,2519367,2683125,2857528,3043267,3241079,3451749,3676112,3915059,4169537,4440556,4729192,5036589,5363967,5712624,6083944,6479400,6900561,7349097,7826788,8335529,8877338,9454364,10068897,10723375,11420394,12162719,12953295,13795259,14691950,15646926,16663976,17747134,18900697,20129242,21437642,22777494,24201087,25713654,27320757,29028304,30842573,32770233,34818372,36994520,39306677,41763344,44373553,47146900,50093581,53224429,56550955,60085389,63840725,67830770,72070193,76574580,81360491,86445521,91848366,97588888,103688193,110168705,117054249,124370139,132143272,138750435,145687956,152972353,160620970,168652018,177084618,185938848,195235790,204997579,215247457,226009829,237310320,249175836,261634627,274716358,288452175,302874783,318018522,333919448,350615420,368146191,386553500,405881175,426175233,447483994,469858193,493351102,518018657,543919589,571115568,2207026470,2471869646,2768494003,3100713283,3472798876,3889534741,4356278909,4879032378,5464516263,6120258214,7956335678,8831532602,9803001188,10881331318,12078277762,15701761090,17114919588,18655262350,20334235961,22164317197,28813612356,30830565220,32988704785,35297914119,37768768107,49099398539,52536356436,56213901386,60148874483,64359295696,83667084404,86177096936,88762409844,91425282139,94168040603,122418452783,126091006366,129873736556,133769948652,137783047111,179117961244,184491500081,190026245083,195727032435,201598843408,262078496430,269940851322,278039076861,286380249166,294971656640,442457484960,455731209508,469403145793,483485240166,497989797370,512929491291,528317376029,544166897309,560491904228,577306661354,1731919984062,1749239183902,1766731575741,1784398891498,1802242880412,2342915744535,2366344901980,2390008350999,2413908434508,2438047518853,5412465491851,5466590146770,5521256048237,5576468608720,5632233294807,11377111255510,12514822381061,13766304619167,15142935081084,16657228589191,33647601750165,37012361925183,40713598117701,44784957929471,49263453722418,99512176519285,109463394171214,120409733588335,132450706947169,145695777641885,294305470836608,323736017920269,356109619712296,391720581683526,430892639851879,870403132500795,957443445750874,1053187790325960,1158506569358560,1737759854037840]
def get_perecent(level, exp):
    if level==0:
        return 0
    else:
        return 100*exp/exp_table[level-1]
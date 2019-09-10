
#include "TH1.h"
#include "TF1.h"
#include "TArray.h"
#include "TCanvas.h"
#include "TObjArray.h"

#include <boost/math/distributions/skew_normal.hpp>

TString from_env(TString env_var,TString default_val){
  if(gSystem->Getenv(env_var)){
    return gSystem->Getenv(env_var);
  } 
  return default_val;
}

Float_t from_env_float(TString env_var,TString default_val){
  TString val = default_val;
  if(gSystem->Getenv(env_var)){
    val = gSystem->Getenv(env_var);
  } 
  return val.Atof();
}

Int_t from_env_int(TString env_var,TString default_val){
  TString val = default_val;
  if(gSystem->Getenv(env_var)){
    val = gSystem->Getenv(env_var);
  } 
  return val.Atoi();
}


Int_t mcol(Int_t i){
  const Int_t wheel_size = 7;
  Int_t wheel[wheel_size] = {kBlack, kRed, kBlue, kGreen, kMagenta +1, kCyan +1, kYellow +1};
//   i+=wheel_size;
  if(i % wheel_size == 0){ // a blackish color
    if(i/wheel_size == 0)
      return kBlack;
    if(i/wheel_size == 1)
      return kGray+3;
    if(i/wheel_size == 2)
      return kGray+2;
    if(i/wheel_size == 3)
      return kGray+1;
    if(i/wheel_size == 4)
      return kGray;
  }
  return wheel[i%wheel_size] + i/wheel_size; 
}

// for compatibility for analysis scripts from 2016 ...
void hist_to_tarrayf(TH1* hist, TArrayF* xarr, TArrayF* yarr){
  
  Float_t x,y;
  
  for (Int_t i = 1 ; i <= hist->GetEntries(); i++){
  
    x = hist->GetXaxis()->GetBinCenter(i);
    y = hist->GetBinContent(i);
    xarr->AddAt(x,i-1);
    yarr->AddAt(y,i-1);
  
  }
  xarr->Set(hist->GetEntries());
  yarr->Set(hist->GetEntries());

  
}

TH1F* gaus_conv(TH1F* hist,Float_t sigma){
  
  Float_t range = 5*sigma;
  
  TF1* my_gaus = new TF1("my_gaus", "gaus",-range,+range);
  
  TH1F* conv_hist = (TH1F*) hist->Clone();
  conv_hist->SetName(Form("%s_conv_gaus_%3.2f",hist->GetName(),sigma));
  conv_hist->SetTitle(Form("%s_conv_gaus_%3.2f",hist->GetName(),sigma));
  
  my_gaus->SetParameter(0,1/(TMath::Sqrt(TMath::TwoPi())*sigma) );
  my_gaus->SetParameter(1,0);
  my_gaus->SetParameter(2,sigma);
  
  Float_t weight = (conv_hist->GetXaxis()->GetXmax() - conv_hist->GetXaxis()->GetXmin())/((Float_t) conv_hist->GetNbinsX());
  
  for (Int_t i =1; i<=conv_hist->GetNbinsX();++i){
    Float_t xpos = conv_hist->GetBinCenter(i);
    conv_hist->SetBinContent(i,0);
    
    for (Int_t j=1; j<=hist->GetNbinsX();++j){
      Float_t xpos_ = hist->GetBinCenter(j);
      Float_t rel_x = xpos_ -xpos;
      if( abs(rel_x)<range){
        conv_hist->SetBinContent(i,conv_hist->GetBinContent(i)+
                                 weight * hist->GetBinContent(j)*my_gaus->Eval(rel_x) );
      }
    }
//     conv_hist->SetBinError(i,0);
    
  }
  
  return conv_hist;
  
}

TH1* fftconvolve(TH1D* h1, TH1D* h2){
  
  
  Int_t samples = h1->GetEntries();
  
  TVirtualFFT *fft_h1 = TVirtualFFT::FFT(1, &samples, "R2C M K");
  fft_h1->SetPoints(h1->GetArray());
  fft_h1->Transform();
  
  TVirtualFFT *fft_h2 = TVirtualFFT::FFT(1, &samples, "R2C M K");
  fft_h2->SetPoints(h2->GetArray());
  fft_h2->Transform();
 
  Double_t *re_h1 = new Double_t[samples];
  Double_t *im_h1 = new Double_t[samples];
  fft_h1->GetPointsComplex(re_h1,im_h1);
  
  Double_t *re_h2 = new Double_t[samples];
  Double_t *im_h2 = new Double_t[samples];
  fft_h2->GetPointsComplex(re_h2,im_h2);
 
  
  Double_t *re_conv = new Double_t[samples];
  Double_t *im_conv = new Double_t[samples];
 
  for (Int_t i = 0; i<samples; i++){
    // complex multiplication ... element wise
    re_conv[i] = re_h1[i]*re_h2[i] - im_h1[i]*im_h2[i];
    im_conv[i] = im_h1[i]*re_h2[i] + re_h1[i]*im_h2[i];
  }
  
  TVirtualFFT *fft_back = TVirtualFFT::FFT(1, &samples, "C2R M K");
  fft_back->SetPointsComplex(re_conv,im_conv);
  fft_back->Transform();
  
  TH1 *hback = 0;
  hback = TH1::TransformHisto(fft_back,hback, "RE");
  hback->GetXaxis()->SetLimits(
    h1->GetXaxis()->GetXmin(),
    h1->GetXaxis()->GetXmax()
  );
  delete fft_h1;
  delete fft_h2;
  delete fft_back;
  
  return hback;
}


Float_t skew_norm(Float_t x, Float_t location, Float_t scale, Float_t shape){
  
  if(scale <0.001)
    scale=0.001;
  
  if(shape <0.001)
    shape=0.001;
  
  boost::math::skew_normal_distribution<Float_t> dist(location,scale,shape);
  return boost::math::pdf(dist,x);
  
}

Float_t my_skew_norm(Float_t x, Float_t location, Float_t scale, Float_t shape){
  return TMath::Gaus( (x-location) - TMath::Exp(-(-1+shape*(x-location))),0,scale);
  
}

TArrayF* fit_skewed(TH1* hist){
  TArrayF* return_vals = new TArrayF(6);
  
  Float_t hist_mean = hist->GetMean();
  
  TF1 *fit  = new TF1 ("fit","[0]*skew_norm(x,[1],[2],[3])+0*[4]+0*[5]"
                               ,hist_mean-20,hist_mean+20);
  fit->SetParName(0,"const");
  fit->SetParName(1,"location");
  fit->SetParName(2,"scale");
  fit->SetParName(3,"shape");
  fit->SetParName(4,"mean");
  fit->SetParName(5,"stddev");
  fit->FixParameter(4,0);
  fit->FixParameter(5,0);
  
  fit->SetParameter(1,hist_mean);
  fit->SetParLimits(1,hist_mean-20,hist_mean+20);
  fit->SetParameter(2,hist->GetStdDev());
  fit->SetParLimits(2,hist->GetStdDev()/2,hist->GetStdDev()*2);
  fit->FixParameter(3,2.2);
  hist->Fit("fit","WW q");
  fit->ReleaseParameter(3);
  hist->Fit("fit","WW M q");
  
  
  
  
  Float_t constant = fit->GetParameter(0);
  Float_t location = fit->GetParameter(1);
  Float_t scale = fit->GetParameter(2);
  Float_t shape = fit->GetParameter(3);
  
  Float_t delta = shape/TMath::Sqrt(1+shape*shape);
  Float_t fit_mean  = location + scale*delta*TMath::Sqrt(2/TMath::Pi());
  Float_t fit_stddev = scale*TMath::Sqrt(1-2*delta*delta/TMath::Pi());
  
  
  return_vals->SetAt(fit->GetParameter(0),0);
  return_vals->SetAt(location,1);
  return_vals->SetAt(scale,2);
  return_vals->SetAt(shape,3);
  
  return_vals->SetAt(fit_mean,4);
  return_vals->SetAt(fit_stddev,5);
  
  fit->FixParameter(0,constant);
  fit->FixParameter(1,location);
  fit->FixParameter(2,scale);
  fit->FixParameter(3,shape);
  
  fit->FixParameter(4,fit_mean);
  fit->FixParameter(5,fit_stddev);
  
  hist->Fit("fit","q");
  
  return return_vals;
  
}


TObjArray* my_fit_slices_y(TH2F* hist, Float_t t1_noise){
  
  TObjArray* return_objects = new TObjArray();
  TH1F* means = new TH1F(Form("%s%s",hist->GetName(),"_mean"),Form("%s%s",hist->GetName(),"_mean"),hist->GetNbinsX(),hist->GetXaxis()->GetXmin(),hist->GetXaxis()->GetXmax());
  TH1F* stddevs = new TH1F(Form("%s%s",hist->GetName(),"_stddev"),Form("%s%s",hist->GetName(),"_stddev"),hist->GetNbinsX(),hist->GetXaxis()->GetXmin(),hist->GetXaxis()->GetXmax());
  TH1F* fit_means = new TH1F(Form("%s%s",hist->GetName(),"_fit_mean"),Form("%s%s",hist->GetName(),"_fit_mean"),hist->GetNbinsX(),hist->GetXaxis()->GetXmin(),hist->GetXaxis()->GetXmax());
  TH1F* fit_stddevs = new TH1F(Form("%s%s",hist->GetName(),"_fit_stddev"),Form("%s%s",hist->GetName(),"_fit_stddev"),hist->GetNbinsX(),hist->GetXaxis()->GetXmin(),hist->GetXaxis()->GetXmax());
  
  
  
  for (Int_t i = 1; i<= hist->GetNbinsX(); ++i){
    TH1F *py = (TH1F*) hist->ProjectionY("py", i,i); // where firstXbin = 0 and lastXbin = 9
    if(t1_noise > 0){
      py = gaus_conv(py,t1_noise);
    }
//   //   fit->SetParameter(0,py->GetBinContent(py->GetMaximumBin()) );
//   //   fit->SetParLimits(0,0,py->GetBinContent(py->GetMaximumBin())*2 );
//     fit->SetParameter(1,py->GetMean());
//     fit->SetParLimits(1,py->GetMean()-20,py->GetMean()+20);
//     fit->SetParameter(2,py->GetStdDev());
//     fit->SetParLimits(2,py->GetStdDev()/2,py->GetStdDev()*2);
//     fit->FixParameter(3,2.2);
//     py->Fit("fit","WW q");
//     fit->ReleaseParameter(3);
//     py->Fit("fit","WW M q");
//     
//     
//     Float_t location = fit->GetParameter(1);
//     Float_t scale = fit->GetParameter(2);
//     Float_t shape = fit->GetParameter(3);
//     
//     Float_t delta = shape/TMath::Sqrt(1+shape*shape);
//     Float_t fit_mean  = location + scale*delta*TMath::Sqrt(2/TMath::Pi());
//     Float_t fit_stddev = scale*TMath::Sqrt(1-2*delta*delta/TMath::Pi());
    TArrayF* parms=fit_skewed(py);
    
    means->SetBinContent(i,py->GetMean());
//     means->SetBinError(i,fit->GetParError(1));
//     stddev->SetBinContent(i,fit->GetParameter(2));
//     stddev->SetBinError(i,fit->GetParError(2));
    stddevs->SetBinContent(i,py->GetStdDev());
//     stddevs->SetBinError(i,fit->GetParError(2));
    
    fit_means->SetBinContent(i,parms->GetAt(4));
    fit_means->SetBinError(i,0);
    fit_stddevs->SetBinContent(i,parms->GetAt(5));
    fit_stddevs->SetBinError(i,0);
  }
  
  return_objects->AddLast(fit_means);
  return_objects->AddLast(fit_stddevs);
  return return_objects;
}




//                   _          __                  _   _               #
//                  (_)        / _|                | | (_)              #
//   _ __ ___   __ _ _ _ __   | |_ _   _ _ __   ___| |_ _  ___  _ __    #
//  | '_ ` _ \ / _` | | '_ \  |  _| | | | '_ \ / __| __| |/ _ \| '_ \   #
//  | | | | | | (_| | | | | | | | | |_| | | | | (__| |_| | (_) | | | |  #
//  |_| |_| |_|\__,_|_|_| |_| |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|  #
//                                                                      #
//                                                                      # 






void vw_analysis(TString infile) {
  
  
  
  Float_t sample_width = 1.6e-6/10;
  Int_t samples = 3200/10/2;
  
  
  Bool_t draw_pulses = true;
  
  // for fish
  Int_t nth_electron = 0;
  Int_t e_number_max = 6;
  
  gStyle->SetOptFit(0211);
//   gStyle->SetLineWidth(2);
  
  gRandom->SetSeed(0);
  
  Float_t t1_noise=from_env_float("t1_noise","0");
  
  Float_t fish_z_max=from_env_float("fish_z_max","0");
  
  TString t1_noise_method=from_env("t1_noise_method","random");
  Bool_t add_noise = false;
  if (t1_noise_method == "random")
    add_noise = true;
  if (t1_noise  == 0)
    add_noise = false;
  
  Int_t  primaries=from_env_int("primaries","0");
  
  
  
  Float_t bootstrap_factor=from_env_float("bootstrap_factor","1");
  
  TFile* f_out = new TFile("f_out.root","RECREATE");
  
  TFile* infile_root = new TFile(infile);
  
  TTree* garfield_tree;
  
  infile_root = new TFile(infile);
  garfield_tree = (TTree*) infile_root->Get("data_tree");
  f_out->cd();
  
  
  
  
  
  // process the garfield tracks
  
  Int_t y_pos_bins = 4*30;
  
  TH1D* th_esig = new TH1D("th_esig","th_esig;t(s)",samples,0,sample_width);
  TH1*  th_esig_cum = 0;
  
  Float_t t1_offset = 20;
  TH2F* th2_first_e  = new TH2F("th2_first_e","th2_first_e;y pos (mm);tdrift first electron (ns)",y_pos_bins,-3,3,samples,0-t1_offset,sample_width*1e9-t1_offset);
  TH2F* th2_second_e = new TH2F("th2_second_e","th2_second_e;y pos (mm);tdrift second electron (ns)",y_pos_bins,-3,3,samples,0-t1_offset,sample_width*1e9-t1_offset);
  TH2F* th2_third_e  = new TH2F("th2_third_e","th2_third_e;y pos (mm);tdrift third electron (ns)",y_pos_bins,-3,3,samples,0-t1_offset,sample_width*1e9-t1_offset);
  TH2F* th2_fourth_e = new TH2F("th2_fourth_e","th2_fourth_e;y pos (mm);tdrift fourth electron (ns)",y_pos_bins,-3,3,samples,0-t1_offset,sample_width*1e9-t1_offset);
  TH2F* th2_fifth_e  = new TH2F("th2_fifth_e","th2_fifth_e;y pos (mm);tdrift fifth electron (ns)",y_pos_bins,-3,3,samples,0-t1_offset,sample_width*1e9-t1_offset);
  TH2F* th2_sixth_e  = new TH2F("th2_sixth_e","th2_sixth_e;y pos (mm);tdrift sixth electron (ns)",y_pos_bins,-3,3,samples,0-t1_offset,sample_width*1e9-t1_offset);
 
  
  
  
  TTree* fish_tree = new TTree("fish_tree","fish_tree");
for(Int_t bs = 0; bs < bootstrap_factor; ++bs){
  
  Float_t e_drift_t;
  Float_t x,y,last_y;
  Int_t n,hit_wire;
  Float_t last_n = 1;
  garfield_tree->SetBranchAddress("e_drift_t",&e_drift_t);
  garfield_tree->SetBranchAddress("evt",&n);
  garfield_tree->SetBranchAddress("track_start_x",&x);
  garfield_tree->SetBranchAddress("track_start_y",&y);
  garfield_tree->SetBranchAddress("hit_wire",&hit_wire);
 
  
  
  Float_t e_drift_t_a = 1000;
  Float_t e_drift_t_b = 1000;
  Int_t   e_number = 0;
  fish_tree->Branch("e_drift_t_a",&e_drift_t_a);
  fish_tree->Branch("e_drift_t_b",&e_drift_t_b);
  fish_tree->Branch("e_number",&e_number);
  
  std::vector<Float_t> e_drift_t_a_vec;
  std::vector<Float_t> e_drift_t_b_vec;
  
  if( primaries == 0){
    primaries = garfield_tree->GetEntries();
  }
//   primaries = 1;
  for (Int_t i = 0 ; i < primaries + 1; i++){
    
    
    if(i < primaries){
      garfield_tree->GetEntry(i);
    } else {
      n++; // to trigger last processing
    }
    
    if (n > last_n){

      e_drift_t_a = 1000;
      e_drift_t_b = 1000;
      std::sort(e_drift_t_a_vec.begin(),e_drift_t_a_vec.end());
      std::sort(e_drift_t_b_vec.begin(),e_drift_t_b_vec.end());
      
      for(e_number = 0; e_number < e_number_max; ++e_number){
        if(e_drift_t_a_vec.size() > e_number){
          e_drift_t_a = e_drift_t_a_vec[e_number] + ((add_noise)?gRandom->Gaus(0,t1_noise):0);
        } else {
          e_drift_t_a = 1000;
        }
        if(e_drift_t_b_vec.size() > e_number){
          e_drift_t_b = e_drift_t_b_vec[e_number] + ((add_noise)?gRandom->Gaus(0,t1_noise):0);
        } else {
          e_drift_t_b = 1000;
        }
        fish_tree->Fill();
      }
      
      if(e_drift_t_a_vec.size() > 0){
        th2_first_e->Fill(last_y*1e3,e_drift_t_a_vec[0] + ((add_noise)?gRandom->Gaus(0,t1_noise):0));
      }
      if(e_drift_t_a_vec.size() > 1){
        th2_second_e->Fill(last_y*1e3,e_drift_t_a_vec[1] + ((add_noise)?gRandom->Gaus(0,t1_noise):0));
      }
      if(e_drift_t_a_vec.size() > 2){
        th2_third_e->Fill(last_y*1e3,e_drift_t_a_vec[2] + ((add_noise)?gRandom->Gaus(0,t1_noise):0));
      }
      if(e_drift_t_a_vec.size() > 3){
        th2_fourth_e->Fill(last_y*1e3,e_drift_t_a_vec[3] + ((add_noise)?gRandom->Gaus(0,t1_noise):0));
      }
      if(e_drift_t_a_vec.size() > 4){
        th2_fifth_e->Fill(last_y*1e3,e_drift_t_a_vec[4] + ((add_noise)?gRandom->Gaus(0,t1_noise):0));
      }
      if(e_drift_t_a_vec.size() > 5){
        th2_sixth_e->Fill(last_y*1e3,e_drift_t_a_vec[5] + ((add_noise)?gRandom->Gaus(0,t1_noise):0));
      }
      
      
      e_drift_t_a_vec.clear();
      e_drift_t_b_vec.clear();
      
      if(draw_pulses && n < 100){
        if(last_n == 1){
          th_esig->DrawClone();
        }
      }
      th_esig->Reset();
      
    }
    
    
    
    
    if (hit_wire == 1){
      e_drift_t_a_vec.push_back(e_drift_t*1e9);
    } else if (hit_wire == 2){
      e_drift_t_b_vec.push_back(e_drift_t*1e9);
    }
    
    th_esig->Fill(e_drift_t);
    
    last_n = n;
    last_y = y;
  }
  
}

f_out->cd();




Float_t max_y_sliced_means = 40.;


Float_t t1_conv_noise = 0;
if(t1_noise_method == "conv"){
  t1_conv_noise = t1_noise;
}

TObjArray* first_e_fit_results = my_fit_slices_y(th2_first_e,t1_conv_noise);
TH1F* sliced_means_first_e = (TH1F*) first_e_fit_results->At(0);
TH1F* sliced_sigmas_first_e = (TH1F*) first_e_fit_results->At(1);
sliced_sigmas_first_e->GetYaxis()->SetRangeUser(0,10);
sliced_means_first_e->GetYaxis()->SetRangeUser(0,max_y_sliced_means);

TObjArray* second_e_fit_results = my_fit_slices_y(th2_second_e,t1_conv_noise);
TH1F* sliced_means_second_e = (TH1F*) second_e_fit_results->At(0);
TH1F* sliced_sigmas_second_e = (TH1F*) second_e_fit_results->At(1);
sliced_sigmas_second_e->GetYaxis()->SetRangeUser(0,10);
sliced_means_second_e->GetYaxis()->SetRangeUser(0,max_y_sliced_means);

TObjArray* third_e_fit_results = my_fit_slices_y(th2_third_e,t1_conv_noise);
TH1F* sliced_means_third_e = (TH1F*) third_e_fit_results->At(0);
TH1F* sliced_sigmas_third_e = (TH1F*) third_e_fit_results->At(1);
sliced_sigmas_third_e->GetYaxis()->SetRangeUser(0,10);
sliced_means_third_e->GetYaxis()->SetRangeUser(0,max_y_sliced_means);

TObjArray* fourth_e_fit_results = my_fit_slices_y(th2_fourth_e,t1_conv_noise);
TH1F* sliced_means_fourth_e = (TH1F*) fourth_e_fit_results->At(0);
TH1F* sliced_sigmas_fourth_e = (TH1F*) fourth_e_fit_results->At(1);
sliced_sigmas_fourth_e->GetYaxis()->SetRangeUser(0,10);
sliced_means_fourth_e->GetYaxis()->SetRangeUser(0,max_y_sliced_means);

TObjArray* fifth_e_fit_results = my_fit_slices_y(th2_fifth_e,t1_conv_noise);
TH1F* sliced_means_fifth_e = (TH1F*) fifth_e_fit_results->At(0);
TH1F* sliced_sigmas_fifth_e = (TH1F*) fifth_e_fit_results->At(1);
sliced_sigmas_fifth_e->GetYaxis()->SetRangeUser(0,10);
sliced_means_fifth_e->GetYaxis()->SetRangeUser(0,max_y_sliced_means);

TObjArray* sixth_e_fit_results = my_fit_slices_y(th2_sixth_e,t1_conv_noise);
TH1F* sliced_means_sixth_e = (TH1F*) sixth_e_fit_results->At(0);
TH1F* sliced_sigmas_sixth_e = (TH1F*) sixth_e_fit_results->At(1);
sliced_sigmas_sixth_e->GetYaxis()->SetRangeUser(0,10);
sliced_means_sixth_e->GetYaxis()->SetRangeUser(0,max_y_sliced_means);


Int_t sim_col_offset = 0;

sliced_means_first_e->SetLineColor(mcol(1+sim_col_offset));
sliced_sigmas_first_e->SetLineColor(mcol(1+sim_col_offset));
sliced_means_second_e->SetLineColor(mcol(2+sim_col_offset));
sliced_sigmas_second_e->SetLineColor(mcol(2+sim_col_offset));
sliced_means_third_e->SetLineColor(mcol(3+sim_col_offset));
sliced_sigmas_third_e->SetLineColor(mcol(3+sim_col_offset));
sliced_means_fourth_e->SetLineColor(mcol(4+sim_col_offset));
sliced_sigmas_fourth_e->SetLineColor(mcol(4+sim_col_offset));
sliced_means_fifth_e->SetLineColor(mcol(5+sim_col_offset));
sliced_sigmas_fifth_e->SetLineColor(mcol(5+sim_col_offset));
sliced_means_sixth_e->SetLineColor(mcol(6+sim_col_offset));
sliced_sigmas_sixth_e->SetLineColor(mcol(6+sim_col_offset));

sliced_means_first_e->SetMarkerColor(mcol(1+sim_col_offset));
sliced_sigmas_first_e->SetMarkerColor(mcol(1+sim_col_offset));
sliced_means_second_e->SetMarkerColor(mcol(2+sim_col_offset));
sliced_sigmas_second_e->SetMarkerColor(mcol(2+sim_col_offset));
sliced_means_third_e->SetMarkerColor(mcol(3+sim_col_offset));
sliced_sigmas_third_e->SetMarkerColor(mcol(3+sim_col_offset));
sliced_means_fourth_e->SetMarkerColor(mcol(4+sim_col_offset));
sliced_sigmas_fourth_e->SetMarkerColor(mcol(4+sim_col_offset));
sliced_means_fifth_e->SetMarkerColor(mcol(5+sim_col_offset));
sliced_sigmas_fifth_e->SetMarkerColor(mcol(5+sim_col_offset));
sliced_means_sixth_e->SetMarkerColor(mcol(6+sim_col_offset));
sliced_sigmas_sixth_e->SetMarkerColor(mcol(6+sim_col_offset));

sliced_means_first_e->SetMarkerStyle(20+1);
sliced_sigmas_first_e->SetMarkerStyle(20+1);
sliced_means_second_e->SetMarkerStyle(20+2);
sliced_sigmas_second_e->SetMarkerStyle(20+2);
sliced_means_third_e->SetMarkerStyle(20+3);
sliced_sigmas_third_e->SetMarkerStyle(20+3);
sliced_means_fourth_e->SetMarkerStyle(20+1);
sliced_sigmas_fourth_e->SetMarkerStyle(20+1);
sliced_means_fifth_e->SetMarkerStyle(20+2);
sliced_sigmas_fifth_e->SetMarkerStyle(20+2);
sliced_means_sixth_e->SetMarkerStyle(20+3);
sliced_sigmas_sixth_e->SetMarkerStyle(20+3);

sliced_means_first_e->SetLineWidth(2);
sliced_sigmas_first_e->SetLineWidth(2);
sliced_means_second_e->SetLineWidth(2);
sliced_sigmas_second_e->SetLineWidth(2);
sliced_means_third_e->SetLineWidth(2);
sliced_sigmas_third_e->SetLineWidth(2);
sliced_means_fourth_e->SetLineWidth(2);
sliced_sigmas_fourth_e->SetLineWidth(2);
sliced_means_fifth_e->SetLineWidth(2);
sliced_sigmas_fifth_e->SetLineWidth(2);
sliced_means_sixth_e->SetLineWidth(2);
sliced_sigmas_sixth_e->SetLineWidth(2);

sliced_means_first_e->SetTitle(  "drift time mean first electron");
sliced_means_second_e->SetTitle( "drift time mean second electron");
sliced_means_third_e->SetTitle(  "drift time mean third electron");
sliced_means_fourth_e->SetTitle( "drift time mean fourth electron");
sliced_means_fifth_e->SetTitle(  "drift time mean fifth electron");
sliced_means_sixth_e->SetTitle(  "drift time mean sixth electron");
sliced_sigmas_first_e->SetTitle( "drift time stdev first electron");
sliced_sigmas_second_e->SetTitle("drift time stdev second electron");
sliced_sigmas_third_e->SetTitle( "drift time stdev third electron");
sliced_sigmas_fourth_e->SetTitle("drift time stdev fourth electron");
sliced_sigmas_fifth_e->SetTitle( "drift time stdev fifth electron");
sliced_sigmas_sixth_e->SetTitle( "drift time stdev sixth electron");



TCanvas* c_means_first_to_sixth = new TCanvas();
// mg_t1_comp->DrawClone("AP");
sliced_means_first_e->DrawClone("L");
sliced_means_second_e->DrawClone("same L");
sliced_means_third_e->DrawClone("same L");
sliced_means_fourth_e->DrawClone("same L");
sliced_means_fifth_e->DrawClone("same L");
sliced_means_sixth_e->DrawClone("same L");

c_means_first_to_sixth->BuildLegend();


TCanvas* c_sigmas_first_to_sixth = new TCanvas();
sliced_sigmas_first_e->DrawClone("L");
sliced_sigmas_second_e->DrawClone("same L");
sliced_sigmas_third_e->DrawClone("same L");
sliced_sigmas_fourth_e->DrawClone("same L");
sliced_sigmas_fifth_e->DrawClone("same L");
sliced_sigmas_sixth_e->DrawClone("same L");

c_sigmas_first_to_sixth->BuildLegend();



TCanvas* c_first_to_sixth = new TCanvas();
c_first_to_sixth->Divide(3,2);
c_first_to_sixth->cd(1);
th2_first_e->Draw("colz");
c_first_to_sixth->cd(2);
th2_second_e->Draw("colz");
c_first_to_sixth->cd(3);
th2_third_e->Draw("colz");
c_first_to_sixth->cd(4);
th2_fourth_e->Draw("colz");
c_first_to_sixth->cd(5);
th2_fifth_e->Draw("colz");
c_first_to_sixth->cd(6);
th2_sixth_e->Draw("colz");

TCanvas* fish_canvas = new TCanvas();
fish_canvas->Divide(3,2);
// draw a fish
for (Int_t i = 0; i < 6; ++i){
  fish_canvas->cd(i+1);
  fish_tree->Draw(Form("(e_drift_t_b-e_drift_t_a):(e_drift_t_b+e_drift_t_a)>>fish%d(250,-200,300,200,-100,100)",i),
                  Form("e_drift_t_b <1000 && e_number == %d",i),"colz");
  TH2F* this_fish = (TH2F*) f_out->Get(Form("fish%d",i));
  this_fish->SetMinimum(0);
  if(fish_z_max)
    this_fish->SetMaximum(fish_z_max);
  this_fish->GetXaxis()->SetRangeUser(-50,200);
  
}

TCanvas* fish_proj_canvas = new TCanvas();
fish_proj_canvas->Divide(3,2);
// draw a fish
for (Int_t i = 0; i < 6; ++i){
  fish_proj_canvas->cd(i+1);
  fish_tree->Draw(Form("(e_drift_t_b+e_drift_t_a)>>fish_proj%d(250,-200,300,200,-100,100)",i),
                  Form("abs(e_drift_t_b - e_drift_t_a) < 5 && e_drift_t_b <1000 && e_number == %d",i),"colz");
  TH1F* this_fish = (TH1F*) f_out->Get(Form("fish_proj%d",i));
  if(t1_noise_method == "conv" && t1_noise > 0){
    this_fish = gaus_conv(this_fish,t1_noise);
  }
  this_fish->GetXaxis()->SetRangeUser(-50,200);
//   this_fish->Fit("fit","WW q M");
  fit_skewed(this_fish);  
}



// TCanvas* vw_canv = new TCanvas("vw_canv","vw_canv",1600,700); 
// vw_canv->Divide(2,1);
// vw_canv->cd(1);
// 
// // mg_t1_comp->GetXaxis()->SetLimits(-2.6,2.6);
// // mg_t1_comp->DrawClone("AP");
// sliced_means_first_e->DrawClone("same L");
// sliced_means_second_e->DrawClone("same L");
// sliced_means_third_e->DrawClone("same L");
// sliced_means_fourth_e->DrawClone("same L");
// sliced_means_fifth_e->DrawClone("same L");
// // TH1F* fourth_scaled = (TH1F*) sliced_means_fourth_e->Clone();
// // fourth_scaled->Scale(0.9);
// // for (Int_t i = 1; i < fourth_scaled->GetNbinsX(); ++i){
// //   fourth_scaled->SetBinError(i,0);
// // }
// // fourth_scaled->Draw("same");
// vw_canv->cd(1)->BuildLegend();
// 
// vw_canv->cd(2);
// // mg_sigma_comp->GetXaxis()->SetLimits(-2.6,2.6);
// // mg_sigma_comp->DrawClone("AP");
// sliced_sigmas_first_e->DrawClone("same L");
// sliced_sigmas_second_e->DrawClone("same L");
// sliced_sigmas_third_e->DrawClone("same L");
// sliced_sigmas_fourth_e->DrawClone("same L");
// sliced_sigmas_fifth_e->DrawClone("same L");
// vw_canv->cd(2)->BuildLegend();

// th2_first_e_0->Draw(); // draw the first fit parameter (constant, in this case)
// new TCanvas();
// th2_first_e_1->Draw(); // draw the second fit parameter (mean, in this case)
// new TCanvas();
// th2_first_e_2->Draw(); // draw the third fit parameter (sigma, in this case)



TCanvas* slice_fit_canvas = new TCanvas();
slice_fit_canvas->Divide(4,5);
// draw a fish
Int_t slice_fit_canvas_pad=1;
for (Int_t i = 10; i < 30; ++i){
  slice_fit_canvas->cd(slice_fit_canvas_pad++);
  TH1F *py = (TH1F*) th2_fourth_e->ProjectionY("py", i,i)->Clone(); // where firstXbin = 0 and lastXbin = 9
  
//   if(t1_noise_method == "conv" && t1_noise > 0){
//     py = gaus_conv(py,t1_noise);
//   }
  
  py->Draw();
  
// //   fit->SetParameter(0,py->GetBinContent(py->GetMaximumBin()) );
// //   fit->SetParLimits(0,0,py->GetBinContent(py->GetMaximumBin())*2 );
//   fit->SetParameter(1,py->GetMean());
//   fit->SetParLimits(1,py->GetMean()-20,py->GetMean()+20);
//   fit->SetParameter(2,py->GetStdDev());
//   fit->SetParLimits(2,py->GetStdDev()/2,py->GetStdDev()*2);
//   fit->FixParameter(3,2.2);
//   py->Fit("fit","WW q");
//   fit->ReleaseParameter(3);
//   py->Fit("fit","WW q M");
  TArrayF* parms= fit_skewed(py);
  py->GetXaxis()->SetRangeUser(parms->GetAt(4)-20,parms->GetAt(4)+20);
  
}



f_out->Write();


  
}


#include "TH1.h"
#include "TF1.h"
#include "TArray.h"
#include "TCanvas.h"
#include "TObjArray.h"

// #include <boost/math/distributions/skew_normal.hpp>

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




void plot_drift_data(TString infile) {
  
  
  
  TFile* f_out = new TFile("f_out.root","RECREATE");
  
  TFile* infile_root = new TFile(infile);
  
  TTree* data_tree = (TTree*) infile_root->Get("data_tree");
  
  f_out->cd();
  
  
  
//   new TCanvas();
//   data_tree->Draw("e_drift_t >> tdrift_h()");
  
  new TCanvas();
  data_tree->Draw("e_drift_t*1e9:e_start_x*1000 >> tdrift_vs_x(602,-3,3,256,0,102.3)","hit_wire == 1","colz");
  TH2F* tdrift_vs_x = (TH2F*) f_out->Get("tdrift_vs_x");
  tdrift_vs_x->GetXaxis()->SetTitle("x pos (mm)");
  tdrift_vs_x->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_x->SetTitle("drift time vs electron x start position");
  tdrift_vs_x->Draw("colz");
  
  new TCanvas();
  // nice bins!
  data_tree->Draw("e_drift_t*1e9:e_start_z*1000 >> tdrift_vs_z(602,-3,3,256,0,102.3)","hit_wire == 1","colz");
  TH2F* tdrift_vs_z = (TH2F*) f_out->Get("tdrift_vs_z");
  tdrift_vs_z->GetXaxis()->SetTitle("z pos (mm)");
  tdrift_vs_z->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_z->SetTitle("drift time vs electron z start position");
  tdrift_vs_z->Draw("colz");
  
  new TCanvas();
  data_tree->Draw("e_drift_t*1e9:e_start_y*1000 >> tdrift_vs_y(602,-3,3,256,0,102.3)","hit_wire == 1","colz");
  TH2F* tdrift_vs_y = (TH2F*) f_out->Get("tdrift_vs_y");
  tdrift_vs_y->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_y->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_y->SetTitle("drift time vs electron y start position");
  tdrift_vs_y->Draw("colz");
  
  new TCanvas();
  data_tree->Draw("e_drift_t*1e9:track_start_x*1000 >> tdrift_vs_track_x(602,-3,3,256,0,102.3)","hit_wire == 1","colz");
  TH2F* tdrift_vs_track_x = (TH2F*) f_out->Get("tdrift_vs_track_x");
  tdrift_vs_track_x->GetXaxis()->SetTitle("x pos (mm)");
  tdrift_vs_track_x->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_x->SetTitle("drift time vs track x position");
  tdrift_vs_track_x->Draw("colz");
  
  
  new TCanvas();
  data_tree->Draw("e_drift_t*1e9:track_start_y*1000 >> tdrift_vs_track_y(602,-3,3,256,0,102.3)","hit_wire == 1","colz");
  TH2F* tdrift_vs_track_y = (TH2F*) f_out->Get("tdrift_vs_track_y");
  tdrift_vs_track_y->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_track_y->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_y->SetTitle("drift time vs track y position");
  tdrift_vs_track_y->Draw("colz");
  
TCanvas* c_elno_1_to_6 = new TCanvas();
c_elno_1_to_6->Divide(3,2);
c_elno_1_to_6->cd(1);
  data_tree->Draw("e_drift_t*1e9:track_start_y*1000 >> tdrift_vs_track_y_el0(602,-3,3,256,0,102.3)","hit_wire == 1 && e_number == 0","colz");
  TH2F* tdrift_vs_track_y_el0 = (TH2F*) f_out->Get("tdrift_vs_track_y_el0");
  tdrift_vs_track_y_el0->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_track_y_el0->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_y_el0->SetTitle("drift time vs track x position, electron 0");
  tdrift_vs_track_y_el0->Draw("colz");
c_elno_1_to_6->cd(2);
  data_tree->Draw("e_drift_t*1e9:track_start_y*1000 >> tdrift_vs_track_y_el1(602,-3,3,256,0,102.3)","hit_wire == 1 && e_number == 1","colz");
  TH2F* tdrift_vs_track_y_el1 = (TH2F*) f_out->Get("tdrift_vs_track_y_el1");
  tdrift_vs_track_y_el1->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_track_y_el1->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_y_el1->SetTitle("drift time vs track x position, electron 1");
  tdrift_vs_track_y_el1->Draw("colz");
c_elno_1_to_6->cd(3);
  data_tree->Draw("e_drift_t*1e9:track_start_y*1000 >> tdrift_vs_track_y_el2(602,-3,3,256,0,102.3)","hit_wire == 1 && e_number == 2","colz");
  TH2F* tdrift_vs_track_y_el2 = (TH2F*) f_out->Get("tdrift_vs_track_y_el2");
  tdrift_vs_track_y_el2->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_track_y_el2->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_y_el2->SetTitle("drift time vs track x position, electron 2");
  tdrift_vs_track_y_el2->Draw("colz");
c_elno_1_to_6->cd(4);
  data_tree->Draw("e_drift_t*1e9:track_start_y*1000 >> tdrift_vs_track_y_el3(602,-3,3,256,0,102.3)","hit_wire == 1 && e_number == 3","colz");
  TH2F* tdrift_vs_track_y_el3 = (TH2F*) f_out->Get("tdrift_vs_track_y_el3");
  tdrift_vs_track_y_el3->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_track_y_el3->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_y_el3->SetTitle("drift time vs track x position, electron 3");
  tdrift_vs_track_y_el3->Draw("colz");
c_elno_1_to_6->cd(5);
  data_tree->Draw("e_drift_t*1e9:track_start_y*1000 >> tdrift_vs_track_y_el4(602,-3,3,256,0,102.3)","hit_wire == 1 && e_number == 4","colz");
  TH2F* tdrift_vs_track_y_el4 = (TH2F*) f_out->Get("tdrift_vs_track_y_el4");
  tdrift_vs_track_y_el4->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_track_y_el4->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_y_el4->SetTitle("drift time vs track x position, electron 4");
  tdrift_vs_track_y_el4->Draw("colz");
c_elno_1_to_6->cd(6);
  data_tree->Draw("e_drift_t*1e9:track_start_y*1000 >> tdrift_vs_track_y_el5(602,-3,3,256,0,102.3)","hit_wire == 1 && e_number == 5","colz");
  TH2F* tdrift_vs_track_y_el5 = (TH2F*) f_out->Get("tdrift_vs_track_y_el5");
  tdrift_vs_track_y_el5->GetXaxis()->SetTitle("y pos (mm)");
  tdrift_vs_track_y_el5->GetYaxis()->SetTitle("drift time (ns)");
  tdrift_vs_track_y_el5->SetTitle("drift time vs track x position, electron 5");
  tdrift_vs_track_y_el5->Draw("colz");

  
}

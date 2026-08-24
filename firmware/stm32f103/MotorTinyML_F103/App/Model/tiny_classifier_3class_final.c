#include "tiny_classifier_3class_final.h"
#include "tiny_classifier_3class_final_params.h"
#include <math.h>
void TinyClassifier3Final_ExtractFeatures(const int16_t raw[200][3], float out[21]) {
  for (int axis=0; axis<3; ++axis) { float sum=0.0f, sq=0.0f, var=0.0f, mad=0.0f;
    int16_t lo=raw[0][axis], hi=lo;
    for (int i=0;i<200;++i) { float v=(float)raw[i][axis]; sum+=v; sq+=v*v; if(raw[i][axis]<lo)lo=raw[i][axis]; if(raw[i][axis]>hi)hi=raw[i][axis]; }
    float mean=sum/200.0f; for(int i=0;i<200;++i){float d=(float)raw[i][axis]-mean;var+=d*d;mad+=fabsf(d);}
    int b=axis*7; out[b]=mean; out[b+1]=sqrtf(var/200.0f); out[b+2]=sqrtf(sq/200.0f); out[b+3]=(float)lo; out[b+4]=(float)hi; out[b+5]=(float)hi-(float)lo; out[b+6]=mad/200.0f;
  }
}
int TinyClassifier3Final_Predict(const float features[21], float scores[3]) { int best=0; float best_score=-INFINITY;
  for(int c=0;c<3;++c){float score=g_tiny3_final_logreg_bias[c]; for(int i=0;i<21;++i){float z=(features[i]-g_tiny3_final_feature_mean[i])/g_tiny3_final_feature_std[i]; score+=g_tiny3_final_logreg_weights[c][i]*z;} scores[c]=score; if(score>best_score){best_score=score;best=c;}} return best;
}

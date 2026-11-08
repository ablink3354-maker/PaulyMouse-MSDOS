package mx.retro.pauly;

import android.app.Activity;
import android.os.Bundle;
import android.net.Uri;
import android.content.Intent;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.Gravity;
import android.graphics.drawable.GradientDrawable;
import android.widget.FrameLayout;
import android.widget.Button;
import android.webkit.*;
import java.io.*;
import java.util.*;

/** Local educational museum. All media are packaged in the APK. */
public class MuseumActivity extends Activity {
 private WebView web;
 private void immersive() {
  if (android.os.Build.VERSION.SDK_INT >= 30) {
   getWindow().setDecorFitsSystemWindows(false);
   WindowInsetsController c=getWindow().getInsetsController();
   if(c!=null){c.hide(WindowInsets.Type.systemBars());c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);}
  } else getWindow().getDecorView().setSystemUiVisibility(5894);
 }
 @Override public void onCreate(Bundle b) {
  super.onCreate(b);
  setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE);
  FrameLayout page=new FrameLayout(this);
  web=new WebView(this);web.setBackgroundColor(0xfffaf8f1);page.addView(web,new FrameLayout.LayoutParams(-1,-1));
  Button home=new Button(this);home.setText("‹ Inicio");home.setAllCaps(false);home.setTextSize(13);home.setTextColor(0xffffefbb);home.setContentDescription("Volver al menú principal");home.setPadding(0,0,0,0);home.setMinHeight(0);home.setMinimumHeight(0);
  GradientDrawable pill=new GradientDrawable();pill.setColor(0xee173e32);pill.setCornerRadius(24*getResources().getDisplayMetrics().density);pill.setStroke(1,0xffd5b56d);home.setBackground(pill);home.setElevation(5*getResources().getDisplayMetrics().density);
  float density=getResources().getDisplayMetrics().density;FrameLayout.LayoutParams hp=new FrameLayout.LayoutParams(Math.round(86*density),Math.round(36*density),Gravity.BOTTOM|Gravity.END);hp.rightMargin=Math.round(12*density);hp.bottomMargin=Math.round((getResources().getConfiguration().screenWidthDp<720?76:12)*density);page.addView(home,hp);
  home.setOnClickListener(v->{web.evaluateJavascript("document.querySelectorAll('audio,video').forEach(function(m){m.pause()})",null);startActivity(new Intent(this,PaulyLauncher.class).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP));finish();});
  setContentView(page);immersive();
  WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);
  s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setMediaPlaybackRequiresUserGesture(true);
  s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);s.setSupportMultipleWindows(false);
  web.setWebViewClient(new WebViewClient(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView v,WebResourceRequest r){
    Uri u=r.getUrl();
    if(!"https".equals(u.getScheme())||!"pauly.local".equals(u.getHost()))return blocked();
    String p=u.getPath();if(p==null||p.equals("/"))p="/index.html";
    if(p.contains("..")||p.contains("\\"))return blocked();
    try{
     String mime=p.endsWith(".html")?"text/html":p.endsWith(".js")?"application/javascript":p.endsWith(".css")?"text/css":p.endsWith(".json")||p.endsWith(".webmanifest")?"application/json":p.endsWith(".png")?"image/png":p.endsWith(".jpg")?"image/jpeg":p.endsWith(".mp3")?"audio/mpeg":"application/octet-stream";
     InputStream stream=getAssets().open("museum"+p);
     Map<String,String> headers=new HashMap<>();headers.put("Cache-Control","no-cache");headers.put("Content-Security-Policy","default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'none'; object-src 'none'");
     return new WebResourceResponse(mime,mime.startsWith("text/")||mime.contains("javascript")||mime.contains("json")?"UTF-8":null,200,"OK",headers,stream);
    }catch(IOException e){return blocked();}
   }
   @Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){
    Uri u=r.getUrl();if("https".equals(u.getScheme())&&"pauly.local".equals(u.getHost()))return false;
    if(r.hasGesture()&&"https".equals(u.getScheme()))try{startActivity(new Intent(Intent.ACTION_VIEW,u));}catch(Exception ignored){}
    return true;
   }
  });
  web.setWebChromeClient(new WebChromeClient());
  if(b!=null)web.restoreState(b);else web.loadUrl("https://pauly.local/index.html");
 }
 private WebResourceResponse blocked(){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",Collections.emptyMap(),new ByteArrayInputStream(new byte[0]));}
 @Override public void onBackPressed(){web.evaluateJavascript("(function(){var d=document.querySelector('dialog[open]');if(d){d.close();return true;}return false;})()",value->{if(!"true".equals(value)){if(web.canGoBack())web.goBack();else finish();}});}
 @Override protected void onSaveInstanceState(Bundle b){web.saveState(b);super.onSaveInstanceState(b);}
 @Override protected void onPause(){web.evaluateJavascript("document.querySelector('audio').pause()",null);web.onPause();super.onPause();}
 @Override protected void onResume(){super.onResume();if(web!=null)web.onResume();immersive();}
 @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);if(focus)immersive();}
 @Override protected void onDestroy(){if(web!=null){web.stopLoading();web.destroy();}super.onDestroy();}
}



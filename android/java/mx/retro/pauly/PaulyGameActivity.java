package mx.retro.pauly;

import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.SeekBar;
import android.widget.PopupWindow;
import android.media.AudioManager;
import java.lang.reflect.Field;

/** Side controls send the same context-aware keys used by the web edition. */
public class PaulyGameActivity extends org.scummvm.scummvm.ScummVMActivity {
 private final Handler ui=new Handler(Looper.getMainLooper());
 private LinearLayout left,right;
 private PopupWindow leftWindow,rightWindow;
 private FrameLayout content;
 private boolean landingOpened;
 private boolean resumed;
 private final Runnable refreshPanels=new Runnable(){public void run(){
  if(!resumed||content==null)return;
  if(!leftWindow.isShowing()||!rightWindow.isShowing()){lastW=lastH=0;layoutSides(content);}
  left.getRootView().invalidate();right.getRootView().invalidate();
  ui.postDelayed(this,300);
 }};
 private View gameSurface;
 private int lastW,lastH;
 private int dp(float value){return Math.round(value*getResources().getDisplayMetrics().density);}
 private GradientDrawable plate(int color,int stroke,int radius){
  GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));d.setStroke(dp(1),stroke);return d;
 }
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  try{Field f=org.scummvm.scummvm.ScummVMActivity.class.getDeclaredField("_main_surface");f.setAccessible(true);gameSurface=(View)f.get(this);}catch(Exception error){android.util.Log.e("Pauly","No se encontró la superficie del juego",error);}
  content=findViewById(android.R.id.content);
  left=column("PAULY");right=column("EXPLORAR");
  add(left,"Libro",()->sendKey(KeyEvent.KEYCODE_B));
  add(left,"Volver",()->sendKey(KeyEvent.KEYCODE_R));
  add(left,"Lugares",()->sendKey(KeyEvent.KEYCODE_L));
  add(left,"Volumen",this::volume);
  add(right,"Anterior",()->sendKey(KeyEvent.KEYCODE_P));
  add(right,"Siguiente",()->sendKey(KeyEvent.KEYCODE_N));
  add(right,"Ayuda",this::help);
  add(right,"Inicio",this::home);
  // Separate, non-focusable app panels stay above the native GL surface when
  // Director changes movies. Their windows cover only the unused side margins.
  leftWindow=new PopupWindow(left,1,1,false);rightWindow=new PopupWindow(right,1,1,false);
  for(PopupWindow p:new PopupWindow[]{leftWindow,rightWindow}){p.setClippingEnabled(true);p.setInputMethodMode(PopupWindow.INPUT_METHOD_NOT_NEEDED);p.setAttachedInDecor(true);p.setWindowLayoutType(WindowManager.LayoutParams.TYPE_APPLICATION_SUB_PANEL);}
  content.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or_,ob)->layoutSides(content));
  content.post(()->layoutSides(content));
 }
 private LinearLayout column(String title){
  LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setGravity(Gravity.CENTER);panel.setPadding(dp(6),dp(10),dp(6),dp(8));panel.setBackground(plate(0xee183b31,0xff76653e,18));
  TextView label=new TextView(this);label.setText(title);label.setTextColor(0xffedcc80);label.setTypeface(Typeface.DEFAULT,Typeface.BOLD);label.setTextSize(11);label.setGravity(Gravity.CENTER);label.setPadding(0,0,0,dp(7));panel.addView(label,new LinearLayout.LayoutParams(-1,-2));return panel;
 }
 private void add(LinearLayout panel,String label,Runnable action){
  Button b=new Button(this);b.setText(label);b.setTextSize(13);b.setAllCaps(false);b.setTextColor(0xfffff0c6);b.setTypeface(Typeface.DEFAULT,Typeface.BOLD);b.setPadding(dp(2),0,dp(2),0);b.setMinWidth(0);b.setMinimumWidth(0);b.setMinHeight(0);b.setMinimumHeight(0);b.setElevation(dp(3));b.setFocusable(false);b.setContentDescription(label);b.setBackground(plate(0xff675028,0xffc7a766,11));
  LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(48));p.topMargin=dp(5);panel.addView(b,p);b.setOnClickListener(v->action.run());
 }
 private void layoutSides(FrameLayout overlay){
  int w=overlay.getWidth(),h=overlay.getHeight();if(w==0||h==0||w==lastW&&h==lastH)return;lastW=w;lastH=h;
  int margin=Math.max(0,(w-h*4/3)/2);int width=Math.max(dp(66),Math.min(dp(112),margin-dp(10)));int inset=Math.max(dp(3),(margin-width)/2);
  // Give the native surface only the original 4:3 game rectangle. A GL movie
  // transition must never paint over the separate, unused side-control area.
  if(gameSurface!=null&&gameSurface.getLayoutParams() instanceof ViewGroup.MarginLayoutParams){
   ViewGroup.MarginLayoutParams surface=(ViewGroup.MarginLayoutParams)gameSurface.getLayoutParams();
   if(surface.leftMargin!=margin||surface.rightMargin!=margin){surface.leftMargin=margin;surface.rightMargin=margin;gameSurface.setLayoutParams(surface);}
  }
  int buttonHeight=Math.max(dp(34),Math.min(dp(48),(h-dp(80))/5));
  for(LinearLayout panel:new LinearLayout[]{left,right})for(int i=1;i<panel.getChildCount();i++){View child=panel.getChildAt(i);ViewGroup.LayoutParams p=child.getLayoutParams();p.height=buttonHeight;child.setLayoutParams(p);}
  LinearLayout[] panels={left,right};PopupWindow[] windows={leftWindow,rightWindow};
  for(int i=0;i<2;i++){panels[i].measure(View.MeasureSpec.makeMeasureSpec(width,View.MeasureSpec.EXACTLY),View.MeasureSpec.makeMeasureSpec(0,View.MeasureSpec.UNSPECIFIED));int height=panels[i].getMeasuredHeight();int x=i==0?inset:w-inset-width,y=Math.max(0,(h-height)/2);PopupWindow window=windows[i];if(window.isShowing())window.update(x,y,width,height);else{window.setWidth(width);window.setHeight(height);window.showAtLocation(content,Gravity.TOP|Gravity.LEFT,x,y);}}
 }
 private void sendKey(int key){
  if(gameSurface==null){Toast.makeText(this,"El juego todavía se está preparando.",Toast.LENGTH_SHORT).show();return;}
  gameSurface.requestFocus();gameSurface.dispatchKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,key));ui.postDelayed(()->{if(gameSurface!=null)gameSurface.dispatchKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,key));},80);
 }
 private void help(){
  new AlertDialog.Builder(this).setTitle("Explora con Pauly")
   .setMessage("Toca los animales del paisaje para ver sus animaciones.\n\nLibro: abre la ficha del animal; si aún no elegiste uno, abre la primera.\n\nToca la rana del libro para escuchar la explicación. Anterior y Siguiente cambian la ficha o el escenario.\n\nVolver regresa al paisaje. Lugares abre la máquina de destinos. Inicio vuelve a la pantalla principal.")
   .setPositiveButton("Seguir jugando",(d,w)->{if(gameSurface!=null)gameSurface.requestFocus();}).show();
 }
 private void volume(){
  AudioManager audio=(AudioManager)getSystemService(AUDIO_SERVICE);int stream=AudioManager.STREAM_MUSIC;
  LinearLayout box=new LinearLayout(this);box.setPadding(dp(22),dp(10),dp(22),dp(10));
  SeekBar slider=new SeekBar(this);slider.setMax(audio.getStreamMaxVolume(stream));slider.setProgress(audio.getStreamVolume(stream));box.addView(slider,new LinearLayout.LayoutParams(-1,dp(52)));
  slider.setContentDescription("Volumen del juego");slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
   public void onProgressChanged(SeekBar s,int value,boolean user){if(user)audio.setStreamVolume(stream,value,0);}
   public void onStartTrackingTouch(SeekBar s){}public void onStopTrackingTouch(SeekBar s){}
  });
  new AlertDialog.Builder(this).setTitle("Volumen del juego").setView(box).setPositiveButton("Listo",(d,w)->{if(gameSurface!=null)gameSurface.requestFocus();}).show();
 }
 private void home(){
  try{Field f=org.scummvm.scummvm.ScummVMActivity.class.getDeclaredField("_events");f.setAccessible(true);Object events=f.get(this);events.getClass().getMethod("sendQuitEvent").invoke(events);}catch(Exception error){android.util.Log.e("Pauly","No se pudo cerrar el motor",error);Toast.makeText(this,"Espera a que termine la transición y vuelve a tocar Inicio.",Toast.LENGTH_SHORT).show();}
 }
 @Override public void finish(){
  if(landingOpened){super.finish();return;}landingOpened=true;
  runOnUiThread(()->{startActivity(new Intent(this,PaulyLauncher.class).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP));super.finish();});
 }
 @Override public void onPause(){resumed=false;ui.removeCallbacks(refreshPanels);if(leftWindow!=null)leftWindow.dismiss();if(rightWindow!=null)rightWindow.dismiss();super.onPause();}
 @Override public void onResume(){super.onResume();resumed=true;if(content!=null){lastW=lastH=0;content.post(()->layoutSides(content));ui.post(refreshPanels);}}
 @Override public void onWindowFocusChanged(boolean focused){super.onWindowFocusChanged(focused);if(focused&&content!=null){lastW=lastH=0;content.post(()->layoutSides(content));}}
 @Override public void onDestroy(){ui.removeCallbacksAndMessages(null);if(leftWindow!=null)leftWindow.dismiss();if(rightWindow!=null)rightWindow.dismiss();gameSurface=null;super.onDestroy();}
}

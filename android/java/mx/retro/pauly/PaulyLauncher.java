package mx.retro.pauly;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.graphics.Color;
import android.graphics.BitmapFactory;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import java.io.*;
import java.util.zip.*;

/** Installs the original game data privately, then starts the native Director engine. */
public class PaulyLauncher extends Activity {
 private TextView status; private Button play,museum;
 private final String version="es-audio-final-4b";
 private final String trialNotice="Juego y museo sin conexión · Español latino.";
 private int dp(int value){return Math.round(value*getResources().getDisplayMetrics().density);}
 @Override public void onCreate(Bundle state){
  super.onCreate(state);setRequestedOrientation(6);getWindow().getDecorView().setSystemUiVisibility(5894);
  FrameLayout page=new FrameLayout(this);page.setBackgroundColor(Color.rgb(15,40,32));
  ImageView backdrop=new ImageView(this);backdrop.setScaleType(ImageView.ScaleType.CENTER_CROP);
  try(InputStream image=getAssets().open("museum/assets/backgrounds/bosque.png")){backdrop.setImageBitmap(BitmapFactory.decodeStream(image));}catch(IOException ignored){}
  page.addView(backdrop,new FrameLayout.LayoutParams(-1,-1));
  View shade=new View(this);shade.setBackground(new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{0x66102219,0xee102a22}));page.addView(shade,new FrameLayout.LayoutParams(-1,-1));
  LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER);row.setPadding(dp(18),dp(16),dp(22),dp(16));
  ImageView pauly=new ImageView(this);pauly.setContentDescription("Pauly te da la bienvenida");pauly.setScaleType(ImageView.ScaleType.FIT_CENTER);
  try(InputStream image=getAssets().open("museum/assets/pauly.png")){pauly.setImageBitmap(BitmapFactory.decodeStream(image));}catch(IOException ignored){}
  row.addView(pauly,new LinearLayout.LayoutParams(0,-1,0.9f));
  LinearLayout layout=new LinearLayout(this);layout.setOrientation(LinearLayout.VERTICAL);layout.setGravity(Gravity.CENTER);layout.setPadding(dp(12),dp(8),dp(12),dp(8));row.addView(layout,new LinearLayout.LayoutParams(0,-1,1.1f));
  TextView title=new TextView(this);title.setText("Pauly Mouse");title.setTextColor(Color.rgb(255,214,129));title.setTextSize(34);title.setGravity(Gravity.CENTER);layout.addView(title);
  TextView intro=new TextView(this);intro.setText("El mundo animal");intro.setTextColor(Color.WHITE);intro.setTextSize(19);intro.setGravity(Gravity.CENTER);layout.addView(intro);
  play=new Button(this);play.setText("Jugar");play.setTextSize(21);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(dp(280),dp(52));lp.topMargin=dp(14);layout.addView(play,lp);
  museum=new Button(this);museum.setText("Museo de animales");museum.setTextSize(18);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(dp(280),dp(52));mp.topMargin=dp(4);layout.addView(museum,mp);
  styleButton(play,true);styleButton(museum,false);
  status=new TextView(this);status.setText(trialNotice);status.setTextColor(Color.rgb(219,232,210));status.setGravity(Gravity.CENTER);status.setPadding(10,18,10,0);layout.addView(status);
  page.addView(row,new FrameLayout.LayoutParams(-1,-1));setContentView(page);play.setOnClickListener(v->prepare());museum.setOnClickListener(v->startActivity(new Intent(this,MuseumActivity.class)));
 }
 private void styleButton(Button button,boolean primary){
  button.setAllCaps(false);button.setTypeface(Typeface.DEFAULT,Typeface.BOLD);button.setTextColor(primary?0xff183b2d:0xffffedbd);button.setElevation(dp(4));
  GradientDrawable shape=new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,primary?new int[]{0xfff1d084,0xffdcb15d}:new int[]{0xff345e47,0xff193e30});shape.setCornerRadius(dp(15));shape.setStroke(dp(1),0xffc6a35a);button.setBackground(shape);
 }
 private void prepare(){
  play.setEnabled(false);museum.setEnabled(false);status.setText("Preparando los archivos del juego…");
  new Thread(()->{
   try{
    File dir=new File(getFilesDir(),"pauly");File marker=new File(dir,".installed-"+version);
    if(!marker.isFile()){
     if(!dir.isDirectory()&&!dir.mkdirs())throw new IOException("No se pudo crear la carpeta del juego");
     String prefix=dir.getCanonicalPath()+File.separator;byte[] buffer=new byte[65536];int count=0;
     try(ZipInputStream zip=new ZipInputStream(getAssets().open("pauly-game.zip"))){
      ZipEntry entry;while((entry=zip.getNextEntry())!=null){
       File dest=new File(dir,entry.getName());if(!dest.getCanonicalPath().startsWith(prefix))throw new IOException("Ruta de archivo inválida");
       if(entry.isDirectory()){if(!dest.isDirectory()&&!dest.mkdirs())throw new IOException("No se pudo crear una carpeta");continue;}
       File parent=dest.getParentFile();if(!parent.isDirectory()&&!parent.mkdirs())throw new IOException("No se pudo crear una carpeta");
       try(OutputStream out=new FileOutputStream(dest)){int n;while((n=zip.read(buffer))!=-1)out.write(buffer,0,n);}
       if(++count%40==0){final int done=count;runOnUiThread(()->status.setText("Preparando el juego: "+done+" archivos…"));}
      }
     }
     try(OutputStream out=new FileOutputStream(marker)){out.write(version.getBytes("UTF-8"));}
    }
    File ini=new File(getFilesDir(),"scummvm.ini");
    String config="[scummvm]\nversioninfo=2.9.1\ngui_language=es\nandroid_saf_dialog_shown=true\nfullscreen=true\naspect_ratio=true\nfiltering=true\norientation_menus=landscape\norientation_games=landscape\ntouch_mode_menus=mouse\ntouch_mode_2d_games=mouse\nonscreen_control=false\nsubtitles=true\n\n[pauly]\nengineid=director\ngameid=director\nplatform=windows\nlanguage=nl\ndescription=Pauly Mouse\npath="+dir.getAbsolutePath()+"\nextrapath="+new File(dir,"SOUNDS").getAbsolutePath()+"\n";
    try(OutputStream out=new FileOutputStream(ini)){out.write(config.getBytes("UTF-8"));}
    runOnUiThread(()->{play.setEnabled(true);museum.setEnabled(true);status.setText(trialNotice);Intent game=new Intent(this,PaulyGameActivity.class);game.setData(Uri.parse("scummvm:pauly"));startActivity(game);});
   }catch(Exception error){runOnUiThread(()->{play.setEnabled(true);museum.setEnabled(true);status.setText("No se pudo preparar el juego: "+error.getMessage());});}
  },"PaulyDataInstaller").start();
 }
 @Override public void onWindowFocusChanged(boolean focused){super.onWindowFocusChanged(focused);if(focused)getWindow().getDecorView().setSystemUiVisibility(5894);}
}


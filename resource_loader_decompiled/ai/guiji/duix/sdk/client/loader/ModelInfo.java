Compiled from "SourceFile"
public class ai.guiji.duix.sdk.client.loader.ModelInfo implements java.io.Serializable {
  public int a;

  public int b;

  public boolean c;

  public int d;

  public java.lang.String e;

  public java.lang.String f;

  public java.lang.String g;

  public java.lang.String h;

  public ai.guiji.duix.sdk.client.loader.ModelInfo$Region i;

  public java.util.List j;

  public ai.guiji.duix.sdk.client.loader.ModelInfo();
    Code:
       0: aload_0
       1: dup
       2: dup2
       3: dup2
       4: invokespecial #34                 // Method java/lang/Object."<init>":()V
       7: sipush        540
      10: putfield      #36                 // Field a:I
      13: sipush        960
      16: putfield      #38                 // Field b:I
      19: iconst_1
      20: putfield      #40                 // Field c:Z
      23: iconst_0
      24: putfield      #42                 // Field d:I
      27: new           #44                 // class java/util/ArrayList
      30: dup
      31: astore_0
      32: invokespecial #45                 // Method java/util/ArrayList."<init>":()V
      35: aload_0
      36: putfield      #47                 // Field j:Ljava/util/List;
      39: return
    LineNumberTable:
      line 1: 4
      line 3: 10
      line 4: 16
      line 5: 20
      line 7: 24
      line 15: 27

  public int getWidth();
    Code:
       0: aload_0
       1: getfield      #36                 // Field a:I
       4: ireturn
    LineNumberTable:
      line 1: 1

  public void setWidth(int);
    Code:
       0: aload_0
       1: iload_1
       2: putfield      #36                 // Field a:I
       5: return
    LineNumberTable:
      line 1: 2

  public int getHeight();
    Code:
       0: aload_0
       1: getfield      #38                 // Field b:I
       4: ireturn
    LineNumberTable:
      line 1: 1

  public void setHeight(int);
    Code:
       0: aload_0
       1: iload_1
       2: putfield      #38                 // Field b:I
       5: return
    LineNumberTable:
      line 1: 2

  public boolean isHasMask();
    Code:
       0: aload_0
       1: getfield      #40                 // Field c:Z
       4: ireturn
    LineNumberTable:
      line 1: 1

  public void setHasMask(boolean);
    Code:
       0: aload_0
       1: iload_1
       2: putfield      #40                 // Field c:Z
       5: return
    LineNumberTable:
      line 1: 2

  public java.lang.String getUnetbin();
    Code:
       0: aload_0
       1: getfield      #61                 // Field e:Ljava/lang/String;
       4: areturn
    LineNumberTable:
      line 1: 1

  public void setUnetbin(java.lang.String);
    Code:
       0: aload_0
       1: aload_1
       2: putfield      #61                 // Field e:Ljava/lang/String;
       5: return
    LineNumberTable:
      line 1: 2

  public java.lang.String getUnetparam();
    Code:
       0: aload_0
       1: getfield      #66                 // Field f:Ljava/lang/String;
       4: areturn
    LineNumberTable:
      line 1: 1

  public void setUnetparam(java.lang.String);
    Code:
       0: aload_0
       1: aload_1
       2: putfield      #66                 // Field f:Ljava/lang/String;
       5: return
    LineNumberTable:
      line 1: 2

  public java.lang.String getUnetmsk();
    Code:
       0: aload_0
       1: getfield      #70                 // Field g:Ljava/lang/String;
       4: areturn
    LineNumberTable:
      line 1: 1

  public void setUnetmsk(java.lang.String);
    Code:
       0: aload_0
       1: aload_1
       2: putfield      #70                 // Field g:Ljava/lang/String;
       5: return
    LineNumberTable:
      line 1: 2

  public java.lang.String getWenetfn();
    Code:
       0: aload_0
       1: getfield      #74                 // Field h:Ljava/lang/String;
       4: areturn
    LineNumberTable:
      line 1: 1

  public void setWenetfn(java.lang.String);
    Code:
       0: aload_0
       1: aload_1
       2: putfield      #74                 // Field h:Ljava/lang/String;
       5: return
    LineNumberTable:
      line 1: 2

  public ai.guiji.duix.sdk.client.loader.ModelInfo$Region getSilenceRegion();
    Code:
       0: aload_0
       1: getfield      #79                 // Field i:Lai/guiji/duix/sdk/client/loader/ModelInfo$Region;
       4: areturn
    LineNumberTable:
      line 1: 1

  public void setSilenceRegion(ai.guiji.duix.sdk.client.loader.ModelInfo$Region);
    Code:
       0: aload_0
       1: aload_1
       2: putfield      #79                 // Field i:Lai/guiji/duix/sdk/client/loader/ModelInfo$Region;
       5: return
    LineNumberTable:
      line 1: 2

  public java.util.List<ai.guiji.duix.sdk.client.loader.ModelInfo$Region> getMotionRegions();
    Code:
       0: aload_0
       1: getfield      #47                 // Field j:Ljava/util/List;
       4: areturn
    LineNumberTable:
      line 1: 1

  public void setMotionRegions(java.util.List<ai.guiji.duix.sdk.client.loader.ModelInfo$Region>);
    Code:
       0: aload_0
       1: aload_1
       2: putfield      #47                 // Field j:Ljava/util/List;
       5: return
    LineNumberTable:
      line 1: 2

  public int getModelkind();
    Code:
       0: aload_0
       1: getfield      #42                 // Field d:I
       4: ireturn
    LineNumberTable:
      line 1: 1

  public void setModelkind(int);
    Code:
       0: aload_0
       1: iload_1
       2: putfield      #42                 // Field d:I
       5: return
    LineNumberTable:
      line 1: 2

  public java.lang.String toString();
    Code:
       0: new           #92                 // class java/lang/StringBuilder
       3: dup
       4: aload_0
       5: swap
       6: ldc           #94                 // String ModelInfo{hasMask=
       8: invokespecial #96                 // Method java/lang/StringBuilder."<init>":(Ljava/lang/String;)V
      11: getfield      #40                 // Field c:Z
      14: invokevirtual #100                // Method java/lang/StringBuilder.append:(Z)Ljava/lang/StringBuilder;
      17: ldc           #102                // String , modelkind=
      19: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      22: aload_0
      23: getfield      #42                 // Field d:I
      26: invokevirtual #108                // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      29: ldc           #110                // String , width=
      31: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      34: aload_0
      35: getfield      #36                 // Field a:I
      38: invokevirtual #108                // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      41: ldc           #112                // String , height=
      43: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      46: aload_0
      47: getfield      #38                 // Field b:I
      50: invokevirtual #108                // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      53: ldc           #114                // String , unetbin=\'
      55: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      58: aload_0
      59: getfield      #61                 // Field e:Ljava/lang/String;
      62: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      65: ldc           #116                // String \', unetparam=\'
      67: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      70: aload_0
      71: getfield      #66                 // Field f:Ljava/lang/String;
      74: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      77: ldc           #118                // String \', unetmsk=\'
      79: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      82: aload_0
      83: getfield      #70                 // Field g:Ljava/lang/String;
      86: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      89: ldc           #120                // String \', wenetfn=\'
      91: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      94: aload_0
      95: getfield      #74                 // Field h:Ljava/lang/String;
      98: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     101: ldc           #122                // String \', silenceRegion=
     103: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     106: aload_0
     107: getfield      #79                 // Field i:Lai/guiji/duix/sdk/client/loader/ModelInfo$Region;
     110: invokevirtual #125                // Method java/lang/StringBuilder.append:(Ljava/lang/Object;)Ljava/lang/StringBuilder;
     113: ldc           #127                // String , motionRegions=
     115: invokevirtual #105                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     118: aload_0
     119: getfield      #47                 // Field j:Ljava/util/List;
     122: invokevirtual #125                // Method java/lang/StringBuilder.append:(Ljava/lang/Object;)Ljava/lang/StringBuilder;
     125: bipush        125
     127: invokevirtual #130                // Method java/lang/StringBuilder.append:(C)Ljava/lang/StringBuilder;
     130: invokevirtual #132                // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
     133: areturn
    LineNumberTable:
      line 1: 0
}

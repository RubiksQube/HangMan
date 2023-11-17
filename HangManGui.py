import sys
import time as tm
import math as ma
import random as rn


from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QCursor
from PySide6.QtCore import Qt, QTimer, QPoint,QLine, QRect


class Window(QMainWindow):
    
    def __init__(self):
        super().__init__()

        # READING FILE/LIST OF POSSIBLE WORDS
        self.PossibleWords = []
        self.ListOfWords = open("PossibleWords.txt","r",encoding="utf8")

        # CONVERTING FILE INTO A LIST TO PICK FROM
        for word in self.ListOfWords:
            Word = ""
            for char in word:
                if char != "\n":
                    Word += char
            self.PossibleWords.append(Word.upper())

        # CREATING THE ALPHABET TO BE LATER DISPLAY
        self.Alpha = [chr(i).upper() for i in range(97,123)]

        # INITIATING TIME FOR LATER DISPLAY
        self.StartTime = tm.time()
        self.Secs,self.Mins = 1,1

        # PICKING A WORD AND INTIATING THE HANGMAN GAME COMPONENTS
        # Word = "anticonstitutionnellement"
        Word = rn.choice(self.PossibleWords)
        Word = Word.upper()

        self.ToFind = [char for char in Word]
        self.Letters = ["_" for char in Word]
        self.Correct = []
        self.Incorrect = []
        self.Submission = []

        # BASIC VARIABLES
        self.ByPass = False
        
        self.Score = 0
        self.MaxLifes = 11
        self.Lifes = self.MaxLifes
        
        self.Size = 30

        # INITATING MOUSE TRACKING AND VARIABLES
        self.setMouseTracking(True)
        self.CurX,self.CurY = 0,0
        self.Clicks = []

        # MODES
        self.SubmitWrdOrChar = False
        self.GameState = "Running"
        
        self.showFullScreen()
        self.FPS = 1000.0/24.0

        self.Timer = QTimer(self)
        self.Timer.timeout.connect(self.loop)
        self.Timer.start(self.FPS)

    #===================================================================================================
    def paintEvent(self, event):
        
        Painter = QPainter(self)
        Painter.setRenderHint(QPainter.Antialiasing)

        #===================================================================================================        
        # PAGE EN NOIR
        Painter.fillRect(self.rect(),QColor(0,0,0))
        # PAGE EN NOIR
        #===================================================================================================        
        # CADRILLAGE BLEU
        Wi,He = self.width(),self.height()
        Ran,Col = int(Wi/self.Size),int(He/self.Size)

        Painter.setPen(QPen(QColor(0,129,255,100),2,Qt.DotLine))
        for r in range(Ran):
            for c in range(Col):
                Painter.drawRect(r*self.Size,c*self.Size,self.Size,self.Size)
                
                if r == 0:
                    Pt = QPoint((r*self.Size)+(self.Size*0.1),(c*self.Size)+(self.Size*0.8))
                    Painter.drawText(Pt,"("+str(c)+")")
                if c == 0:
                    Pt = QPoint((r*self.Size)+(self.Size*0.1),(c*self.Size)+(self.Size*0.8))
                    Painter.drawText(Pt,"("+str(r)+")")
                
        # CADRILLAGE BLEU
        #===================================================================================================        
        Painter.setFont(QFont("Times",25,10,italic=True))
        #===================================================================================================        
        # SCORE BOARD
        
        Elmnts = self.QRectGenerator(X=24,Y=1,Wid=17,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
        Rect,Pt = Elmnts[0],Elmnts[1]

        Painter.setPen(QPen(QColor(176,34,238,200),3,Qt.SolidLine))

        Painter.fillRect(Rect,QColor(0,0,0))
        Painter.drawRect(Rect)
        Painter.drawText(Pt,"Score : "+str(self.Score))
        # SCORE BOARD
        #===================================================================================================        
        # SWITCH TO SUBMIT MODE BUTTON
        Elmnts = self.QRectGenerator(X=1,Y=15,Wid=8,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
        Rect,Pt = Elmnts[0],Elmnts[1]

        if self.CheckCursor(Rect):
            Painter.setPen(QPen(QColor(255,241,27,200),2,Qt.SolidLine))
        else:
            Painter.setPen(QPen(QColor(0,129,255,200),3,Qt.SolidLine))

        Painter.fillRect(Rect,QColor(0,0,0))
        Painter.drawRect(Rect)
        Painter.drawText(Pt,"Submit a word")

        if self.CheckClick(Rect):
            self.SubmitWrdOrChar = not self.SubmitWrdOrChar
            self.Submission = []
        # SWITCH TO SUBMIT MODE BUTTON 
        #===================================================================================================        
        # SUBMIT ENTRY SPACE
        if self.SubmitWrdOrChar:
            Elmnts = self.QRectGenerator(X=1,Y=19,Wid=33,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
            Rect,Pt = Elmnts[0],Elmnts[1]
            
            Painter.setPen(QPen(QColor(31,163,255),3,Qt.SolidLine))
            
            Painter.fillRect(Rect,QColor(0,0,0))
            Painter.drawRect(Rect)
            Line = " ".join(self.Submission)
            Painter.drawText(Pt,str(Line))
        # SUBMIT ENTRY SPACE
        #===================================================================================================        
        # SUBMIT BUTTON
        if self.SubmitWrdOrChar:
            Elmnts = self.QRectGenerator(X=34,Y=19,Wid=7,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
            Rect,Pt = Elmnts[0],Elmnts[1]
            
            if self.CheckCursor(Rect):
                    Painter.setPen(QPen(QColor(20,171,86,200),2,Qt.SolidLine))
            else:
                Painter.setPen(QPen(QColor(31,255,129),2,Qt.SolidLine))
            
            Painter.fillRect(Rect,QColor(0,0,0))
            Painter.drawRect(Rect)
            Painter.drawText(Pt,"SUBMIT")

            if self.CheckClick(Rect):
                if self.CheckWord(self.Submission):
                    self.GameState = "Win"
                    self.Score += 1
                else:
                    self.Lifes -= 1
        # SUBMIT BUTTON
        #===================================================================================================        
        # WORD BOARD
        Elmnts = self.QRectGenerator(X=1,Y=21,Wid=33,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
        Rect,Pt = Elmnts[0],Elmnts[1]

        Painter.setPen(QPen(QColor(255,137,33,200),3,Qt.SolidLine))
        Painter.fillRect(Rect,QColor(0,0,0))
        Painter.drawRect(Rect)
        
        Line = " ".join(self.Letters)
        Painter.drawText(Pt,str(Line))
        # WORD BOARD
        #===================================================================================================        
        # TIME BOARD
        Elmnts = self.QRectGenerator(X=34,Y=21,Wid=7,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
        Rect,Pt = Elmnts[0],Elmnts[1]
        
        Painter.setPen(QPen(QColor(238,41,41,200),3,Qt.SolidLine))
        Painter.fillRect(Rect,QColor(0,0,0))
        Painter.drawRect(Rect)
        
        Line = ""
        Line += "0"+str(self.Mins) if self.Mins < 10 else str(self.Mins)
        Line += ":"
        Line += "0"+str(self.Secs%60) if self.Secs%60 < 10 else str(self.Secs%60)

        Painter.drawText(Pt,Line)
        # TIME BOARD
        #===================================================================================================        
        # HANG BOARD & HANGMAN
        Elmnts = self.QRectGenerator(X=24,Y=3,Wid=17,Hei=16,PtX=0.3,PtY=1.2,Margin=0.2)
        Rect,Pt = Elmnts[0],Elmnts[1]
        
        Painter.setPen(QPen(QColor(0,129,255,200),3,Qt.SolidLine))
        Painter.fillRect(Rect,QColor(0,0,0))
        Painter.drawRect(Rect)
        
        Light = QPen(QColor(0,208,255,50),3,Qt.SolidLine)
        LgthRope = QPen(QColor(0,208,255,50),4,Qt.DotLine)
        LghtTrig = QPen(QColor(0,208,255,50),10,Qt.SolidLine)
        LghtBody = QPen(QColor(0,208,255,50),8,Qt.SolidLine)

        Full = QPen(QColor(0,208,255,200),3,Qt.SolidLine)
        Rope = QPen(QColor(0,208,255,200),4,Qt.DotLine)
        Trig = QPen(QColor(0,208,255,200),10,Qt.SolidLine) 
        Body = QPen(QColor(0,208,255,200),8,Qt.SolidLine)
        
        Cx = Rect.x()
        Cy = Rect.y()
        N = [Cx+self.Size*(7.5 + 1) ,Cy+self.Size*(4+2)]
        S = [N[0],N[1]+self.Size*0.5]
        H = [N[0],N[1]+self.Size*3]
        A1ang = 52
        A2ang = 48
        L1ang = 52
        L2ang = 48

        # ============================ 11 Lifes : Bases
        Painter.setPen(Full) if self.Lifes < 11 else Painter.setPen(Light)
        Painter.fillRect(QRect(Cx+self.Size*1  ,Cy+self.Size*14  ,self.Size*11  ,self.Size*0.3),QColor(0,208,255,100) if self.Lifes < 11 else QColor(0,208,255,50))
        Painter.drawRect(Cx+self.Size*1  ,Cy+self.Size*14  ,self.Size*11  ,self.Size*0.3)

        # ============================ 10 Lifes : Poteau
        Painter.setPen(Full) if self.Lifes < 10 else Painter.setPen(Light)
        Painter.fillRect(QRect(Cx+self.Size*5 ,Cy+self.Size*1,self.Size*0.3 ,self.Size*13),QColor(0,208,255,100) if self.Lifes < 10 else QColor(0,208,255,50))
        Painter.drawRect(Cx+self.Size*5 ,Cy+self.Size*1,self.Size*0.3 ,self.Size*13)
        
        # ============================ 9 Lifes : Barre
        Painter.setPen(Full) if self.Lifes < 9 else Painter.setPen(Light)
        Painter.fillRect(QRect(Cx+self.Size*4 ,Cy+self.Size*1,self.Size*7 ,self.Size*0.3),QColor(0,208,255,100) if self.Lifes < 9 else QColor(0,208,255,50))
        Painter.drawRect(Cx+self.Size*4 ,Cy+self.Size*1,self.Size*7 ,self.Size*0.3)
        
        # ============================ 8 Lifes : Trig
        Painter.setPen(Trig) if self.Lifes < 8 else Painter.setPen(LghtTrig)
        Painter.drawLine(Cx+self.Size*5.2 ,Cy+self.Size*4 ,Cx+self.Size*7 ,Cy+self.Size*1.2)

        # ============================ 7 Lifes : Rope
        Painter.setPen(Rope) if self.Lifes < 7 else Painter.setPen(LgthRope)
        Painter.drawLine(N[0],N[1]-(self.Size*5),N[0],N[1])
        
        # ============================ 6 Lifes : Tete
        Painter.setPen(Body) if self.Lifes < 6 else Painter.setPen(LghtBody)
        Painter.drawEllipse(QPoint(N[0]-self.Size ,N[1]-self.Size*0.4),self.Size ,self.Size)

        # ============================ 5 Lifes : Spine
        Painter.setPen(Body) if self.Lifes < 5 else Painter.setPen(LghtBody)
        Painter.drawLine(N[0],N[1],H[0],H[1])
        
        # ============================ 4 Lifes : Arm1
        Painter.setPen(Body) if self.Lifes < 4 else Painter.setPen(LghtBody)
        Painter.drawLine(S[0]-6,S[1], S[0]-6 +(ma.cos((A1ang/100)*ma.pi))*100 , S[1]+(ma.sin((A1ang/100)*ma.pi))*100 )
        
        # ============================ 3 Lifes : Arm2
        Painter.setPen(Body) if self.Lifes < 3 else Painter.setPen(LghtBody)
        Painter.drawLine(S[0]+6,S[1], S[0]+6 +(ma.cos((A2ang/100)*ma.pi))*100 , S[1]+(ma.sin((A2ang/100)*ma.pi))*100 )

        # ============================ 2 Lifes : Leg1
        Painter.setPen(Body) if self.Lifes < 2 else Painter.setPen(LghtBody)
        Painter.drawLine(H[0],H[1], H[0]+(ma.cos((L1ang/100)*ma.pi))*100 , H[1]+(ma.sin((L1ang/100)*ma.pi))*100 )
        
        # ============================ 1 Lifes : Leg2 & Eyes
        Painter.setPen(Body) if self.Lifes < 1 else Painter.setPen(LghtBody)
        Painter.drawLine(H[0],H[1], H[0]+(ma.cos((L2ang/100)*ma.pi))*100 , H[1]+(ma.sin((L2ang/100)*ma.pi))*100 )
        if self.Lifes < 1:
            Painter.drawLine(N[0]-6 -45 ,N[1]-6 ,N[0]+6 -45 ,N[1]+6)    # Oeil Droit
            Painter.drawLine(N[0]+6 -45 ,N[1]-6 ,N[0]-6 -45 ,N[1]+6)
            
            Painter.drawLine(N[0]-6 - 30 ,N[1]-6 -7 ,N[0]+6 - 30 ,N[1]+6 -7)    # Oeil Gauche
            Painter.drawLine(N[0]+6 - 30 ,N[1]-6 -7 ,N[0]-6 - 30 ,N[1]+6 -7)
        # HANG BOARD & HANGMAN
        #===================================================================================================        
        # ALPHABET
        StX,X,Y = 1,1,1
        for a in self.Alpha:
            Elmnts = self.QRectGenerator(X=X,Y=Y,Wid=2,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
            Rect,Pt = Elmnts[0],Elmnts[1]
            
            if self.SubmitWrdOrChar == False:
                if a in self.Correct:
                    Painter.setPen(QPen(QColor(42,230,234,200),2,Qt.SolidLine))
                elif a in self.Incorrect:
                    Painter.setPen(QPen(QColor(245,56,56,200),2,Qt.SolidLine))
                elif self.CheckCursor(Rect):
                    Painter.setPen(QPen(QColor(255,241,27,200),2,Qt.SolidLine))
                else:
                    Painter.setPen(QPen(QColor(0,255,0,200),2,Qt.DotLine))
            else:
                if a not in self.Incorrect:
                    if self.CheckCursor(Rect):
                        Painter.setPen(QPen(QColor(254,244,18,200),2,Qt.SolidLine))
                    elif a in self.Correct:
                        Painter.setPen(QPen(QColor(0,255,97),3,Qt.SolidLine))
                    else:
                        Painter.setPen(QPen(QColor(133,255,224),2,Qt.DashDotDotLine))
                else:
                        Painter.setPen(QPen(QColor(0,0,0),2,Qt.SolidLine))
      
            Painter.fillRect(Rect,QColor(0,0,0))
            Painter.drawRect(Rect)
            Painter.drawText(Pt,str(a))

            if self.SubmitWrdOrChar:
                if self.CheckClick(Rect) and a not in self.Incorrect:
                   self.Submission.append(a)
            else:
                if self.CheckClick(Rect) and (a not in self.Incorrect and a not in self.Correct):
                    self.CheckLetter(a)
            
            X += 2
            if X >= 10:
                X = StX + (Y%1.5)
                Y += 2
                    
        # ALPHABET
        #===================================================================================================        
        # CLICKS
        Painter.setPen(QPen(QColor(0,208,255,200),3,Qt.SolidLine))
        for clk in self.Clicks:
            Cx = clk[0]
            Cy = clk[1]
            Painter.drawEllipse(QPoint(Cx,Cy),10,10)
            Painter.drawRect(Cx-8 ,Cy-10 ,16 ,-13)
            Members = [QLine(Cx-15,Cy-8,Cx+15,Cy-8),QLine(Cx-2+4,Cy-2,Cx+2+4,Cy+2),QLine(Cx+2+4,Cy-2,Cx-2+4,Cy+2),QLine(Cx-2-4,Cy-2,Cx+2-4,Cy+2),QLine(Cx+2-4,Cy-2,Cx-2-4,Cy+2)]
            Painter.drawLines(Members)
        # CLICKS
        #===================================================================================================        
        # LIFES
        X = 2
        if self.SubmitWrdOrChar:
            Y = 19
        else:
            Y = 21

        for life in range(self.MaxLifes):
            if life < self.Lifes:
                Painter.setPen(QPen(QColor(0,255,0,200),3,Qt.SolidLine))
            else:
                Painter.setPen(QPen(QColor(245,56,56,200),3,Qt.SolidLine))
            Cx = X * self.Size - (self.Size/2)
            Cy = Y * self.Size - (self.Size/2)
            Painter.drawEllipse(QPoint(Cx,Cy),10,10)    # TETE
            
            Painter.drawRect(Cx-8 ,Cy-10 ,16 ,-13)      # Chapeau
            Members = [QLine(Cx-15,Cy-8,Cx+15,Cy-8),QLine(Cx-2+4,Cy-2,Cx+2+4,Cy+2),QLine(Cx+2+4,Cy-2,Cx-2+4,Cy+2),QLine(Cx-2-4,Cy-2,Cx+2-4,Cy+2),QLine(Cx+2-4,Cy-2,Cx-2-4,Cy+2)]
            Painter.drawLines(Members)
            X += 1
        # LIFES
        #===================================================================================================        
        # VICTORY
        if self.GameState == "Win":
            Sd = 2
            Sx,Sy = 4.5,2
            Coords = [[0,0,1,1],[1,1,1,1],[2,2,1,3],[3,1,1,1],[4,0,1,1],
                      [7,0,2,1],[6,1,1,3],[9,1,1,3],[7,4,2,1],
                      [12,0,1,4],[13,4,2,1],[15,0,1,4],
                      
                      [1,6-0.5,1,3],[2,9-0.5,1,1],[3,6-0.5,1,3],[4,9-0.5,1,1],[5,6-0.5,1,3],
                      [7,6-0.5,3,1],[8,7-0.5,1,2],[7,9-0.5,3,1],
                      [11,6-0.5,1,4],[12,7-0.5,1,1],[13,8-0.5,1,1],[14,6-0.5,1,4]]

            Caract = []
            for co in Coords:
                Caract.append([Sx + (Sd*co[0]),Sy + (Sd*co[1]),Sd*co[2],Sd*co[3],0,0,0.05])
            
            Rects = []
            for carac in Caract:
                Elmnts = self.QRectGenerator(X=carac[0],Y=carac[1],Wid=carac[2],Hei=carac[3],PtX=carac[4],PtY=carac[5],Margin=carac[6])
                Rects.append(Elmnts[0])
            
            Painter.setPen(QPen(QColor(255,236,0),4,Qt.SolidLine))
            Painter.fillRect(self.rect(),QColor(0,0,0,200))

            for Rec in Rects:
                Painter.fillRect(Rec,QColor(0,0,0))
                Painter.drawRect(Rec)

            Pt = self.QRectGenerator(0,22)
            Pt = Pt[1]
            Painter.drawText(Pt,"With the Score of : " + str(self.Score))
        # VICTORY
        #===================================================================================================        
        # DEFEAT
        if self.GameState == "Lose":
            Sd = 2
            Sx,Sy = 4.5,1.5
            Coords = [[0,0,1,1],[1,1,1,1],[2,2,1,3],[3,1,1,1],[4,0,1,1],
                      [7,0,2,1],[6,1,1,3],[9,1,1,3],[7,4,2,1],
                      [12,0,1,4],[13,4,2,1],[15,0,1,4],
                      
                      [0,6-0.5,1,4],[0,10-0.5,3,1],
                      [4,7-0.5,1,3],[5,6-0.5,2,1],[7,7-0.5,1,3],[5,10-0.5,2,1],
                      [10,6-0.5,3,1],[9,7-0.5,1,1],[10,8-0.5,2,1],[12,9-0.5,1,1],[9,10-0.5,3,1],
                      [14,6-0.5,4,1],[15.5,7-0.5,1,4]]

            Caract = []
            for co in Coords:
                Caract.append([Sx + (Sd*co[0]),Sy + (Sd*co[1]),Sd*co[2],Sd*co[3],0,0,0.05])
            
            Rects = []
            for carac in Caract:
                Elmnts = self.QRectGenerator(X=carac[0],Y=carac[1],Wid=carac[2],Hei=carac[3],PtX=carac[4],PtY=carac[5],Margin=carac[6])
                Rects.append(Elmnts[0])
            
            Painter.setPen(QPen(QColor(139,0,255),4,Qt.SolidLine))
            Painter.fillRect(self.rect(),QColor(0,0,0,200))
            for Rec in Rects:
                Painter.fillRect(Rec,QColor(0,0,0))
                Painter.drawRect(Rec)

            Pt = self.QRectGenerator(0,22.5)
            Pt = Pt[1]
            Word = "".join(self.ToFind)
            Painter.drawText(Pt,"The Word was => " + str(Word))
        # DEFEAT
        #===================================================================================================        
        # RESET BUTTON 
        if self.GameState == "Win" or self.GameState == "Lose": 
            Elmnts = self.QRectGenerator(X=38,Y=22,Wid=4,Hei=2,PtX=0.3,PtY=1.2,Margin=0.2)
            Rect,Pt = Elmnts[0],Elmnts[1]

            if self.CheckCursor(Rect):
                Painter.setPen(QPen(QColor(0,131,255,200),3,Qt.SolidLine))
                self.ByPass = True
                if self.CheckClick(Rect):
                    self.Reset()
            else:
                Painter.setPen(QPen(QColor(70,0,255,200),3,Qt.SolidLine))
                self.ByPass = False

            Painter.fillRect(Rect,QColor(0,0,0))
            Painter.drawRect(Rect)
            Painter.drawText(Pt,"Reset")
        # RESET BUTTON 
        #===================================================================================================        
        # CURSEUR
        Painter.setPen(QPen(QColor(245,56,56,200),3,Qt.SolidLine))
        # Painter.drawPoint(Cursor)
        Painter.drawEllipse(QPoint(self.CurX,self.CurY),15,15)
        
        Painter.drawRect(self.CurX-10 ,self.CurY-12 ,20 ,-15)
        Members = [QLine(self.CurX-20 ,self.CurY-10 ,self.CurX+20 ,self.CurY-10),QLine(self.CurX-3+6,self.CurY-3,self.CurX+3+6,self.CurY+3),QLine(self.CurX+3+6,self.CurY-3,self.CurX-3+6,self.CurY+3),QLine(self.CurX-3-6,self.CurY-3,self.CurX+3-6,self.CurY+3),QLine(self.CurX+3-6,self.CurY-3,self.CurX-3-6,self.CurY+3)]
        Painter.drawLines(Members)
        # CURSEUR

        if len(self.Clicks) > 0:
                self.Clicks.pop(0)
        # CURSEUR
    #===================================================================================================
           
    def QRectGenerator(self,X=2,Y=2,Wid=2,Hei=2,PtX=0.3,PtY=1.2,Margin=0):
        Startx = (X * self.Size)  + self.Size * Margin
        Starty = (Y * self.Size)  + self.Size * Margin
        Width  =  self.Size * Wid  - self.Size * (Margin*2)
        Heigth =  self.Size * Hei  - self.Size * (Margin*2)
        
        Rect = QRect(Startx,Starty,Width,Heigth)
        Pt = QPoint(Startx + (self.Size*PtX) , Starty + (self.Size*PtY))
        return [Rect,Pt]

    #===================================================================================================        
    def CheckClick(self,Rct):
        X = Rct.x()
        Y = Rct.y()
        Wi = Rct.width()
        He = Rct.height()

        if len(self.Clicks) > 0:
            Clck = self.Clicks[0]
            if Clck[0] >= X and Clck[0] <= X + Wi and Clck[1] >= Y and Clck[1] <= Y + He:
                self.Clicks.pop(0)
                return True
        return False
                
    def CheckCursor(self,Rect):
        X = Rect.x()
        Y = Rect.y()
        Wi = Rect.width()
        He = Rect.height()
        if self.CurX >= X and self.CurX <= X + Wi and self.CurY >= Y and self.CurY <= Y + He:
            return True
        else:
            return False
        
    def CheckWord(self,Word):
        if Word == self.ToFind:
            return True
        else:
            return False 

    def CheckLetter(self,Char):
        if Char in self.ToFind:
            self.Correct.append(Char)
            self.Score += 1
            for ind in range(len(self.ToFind)):
                if self.ToFind[ind] == Char:
                    self.Letters[ind] = Char
        else:
            self.Incorrect.append(Char)
            self.Lifes -= 1
    #===================================================================================================        

    #===================================================================================================
    def Reset(self):
        self.GameState = "Running"
        Word = rn.choice(self.PossibleWords)
        Word = Word.upper()

        self.ToFind = [char for char in Word]
        self.Letters = ["_" for char in Word]
        self.Correct = []
        self.Incorrect = []
        self.Submission = []
        self.SubmitWrdOrChar = False

        self.Lifes = self.MaxLifes
        self.Score = 0

        self.StartTime = tm.time()
        self.Secs,self.Mins = 1,1

    def AddClick(self,event):
        if self.GameState == "Running" or self.ByPass == True:
            self.Clicks.append([event.globalX(),event.globalY()])
    #===================================================================================================

    #===================================================================================================
    def loop(self):
        self.Time = tm.time()
        self.Secs = int(self.Time-self.StartTime)
        self.Mins = int(self.Secs/60)
        
        if self.CheckWord(self.Letters):
            self.GameState = "Win"

        if self.Lifes == 0:
            self.GameState = "Lose"
        self.update()

    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            if self.Timer.isActive():
                self.Timer.stop()
            else:
                self.Timer.start(self.FPS)
        
    def mouseMoveEvent(self, event):
        self.CurX = event.globalX()
        self.CurY = event.globalY()
 
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.AddClick(event)

App = QApplication(sys.argv)
Jeu = Window()
App.exec()
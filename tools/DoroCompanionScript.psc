Scriptname DoroCompanionScript extends Actor

GlobalVariable mode
Message commands
Sound voice
Bool menuOpen = false
Quest dialogueQuest
Scene dialogueScene

Function Setup()
    mode = Game.GetFormFromFile(0x00000804, "DoroFollower.esp") as GlobalVariable
    voice = Game.GetFormFromFile(0x00000809, "DoroFollower.esp") as Sound
    dialogueQuest = Game.GetFormFromFile(0x0000080C, "DoroFollower.esp") as Quest
    dialogueScene = Game.GetFormFromFile(0x0000080D, "DoroFollower.esp") as Scene
    BlockActivation(false, false)
    AllowPCDialogue(true)
    SetEssential(true)
    SetRelationshipRank(Game.GetPlayer(), 4)
    if mode != None && mode.GetValue() > 0.0
        SetPlayerTeammate(true, false, true)
    endif
    menuOpen = false
    if dialogueQuest != None && !dialogueQuest.IsRunning()
        dialogueQuest.Start()
    endif
    if dialogueQuest != None && dialogueQuest.IsRunning()
        ReferenceAlias speaker = dialogueQuest.GetAlias(0) as ReferenceAlias
        if speaker != None && speaker.GetReference() != Self
            speaker.ForceRefTo(Self)
        endif
    endif
    RegisterForHitEvent(Self)
    RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
    EvaluatePackage()
    StartTimer(3.0, 1)
EndFunction

Event OnInit()
    Setup()
EndEvent

Event OnLoad()
    Setup()
EndEvent

Event Actor.OnPlayerLoadGame(Actor akSender)
    Setup()
EndEvent

Event OnActivate(ObjectReference akActionRef)
    if akActionRef != Game.GetPlayer() || IsInCombat()
        return
    endif
    if dialogueQuest == None || !dialogueQuest.IsRunning()
        Setup()
    endif
    AllowPCDialogue(true)
    if voice != None
        voice.Play(Self)
    endif
    if dialogueQuest == None
        Debug.Notification("Doro: dialogue quest missing from ESP (0.2.5).")
        return
    endif
    if !dialogueQuest.IsRunning()
        Debug.Notification("Doro: quest present but startup failed (0.2.5).")
        return
    endif
    if !IsInDialogueWithPlayer() && dialogueScene != None && !dialogueScene.IsPlaying()
        ; First let native activation select the Greeting and establish the dialogue target.
        ; Default-processing-only prevents a recursive OnActivate event.
        Activate(Game.GetPlayer(), true)
        Utility.Wait(0.15)
        ; If Greeting did not enter the player-dialogue scene, start the bound scene directly.
        if !IsInDialogueWithPlayer() && !dialogueScene.IsPlaying()
            dialogueScene.Start()
        endif
    endif
EndEvent

Function DoCommand(int choice)
    if choice == 10
        mode.SetValue(1.0)
        SetPlayerTeammate(true, false, true)
    elseif choice == 20
        mode.SetValue(2.0)
        SetPlayerTeammate(true, false, true)
    elseif choice == 30
        Utility.Wait(0.5)
        OpenInventory(true)
    elseif choice == 40
        mode.SetValue(0.0)
        SetPlayerTeammate(false)
        StopCombat()
        MoveToMyEditorLocation()
    endif
    EvaluatePackage()
EndFunction

Function AssistAgainst(Actor target)
    if target == None || target == Self || target == Game.GetPlayer()
        return
    endif
    if target.IsDead() || target.IsPlayerTeammate()
        return
    endif
    Faction playerFaction = Game.GetForm(0x0001C21C) as Faction
    if target.IsInFaction(playerFaction) || target.GetRelationshipRank(Game.GetPlayer()) > 0
        return
    endif
    if target.IsHostileToActor(Game.GetPlayer())
        if GetCombatTarget() != target
            StartCombat(target)
        endif
    endif
EndFunction

Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string asMaterialName)
    RegisterForHitEvent(Self)
    AssistAgainst(akAggressor as Actor)
EndEvent

Event OnTimer(int aiTimerID)
    if aiTimerID != 1
        return
    endif
    if mode != None && mode.GetValue() > 0.0
        Actor playerRef = Game.GetPlayer()
        Bool scenePlaying = false
        if dialogueScene != None
            scenePlaying = dialogueScene.IsPlaying()
        endif
        if playerRef.IsInCombat() && !IsInCombat()
            AssistAgainst(playerRef.GetCombatTarget())
        endif
        if mode.GetValue() == 1.0 && !IsInCombat() && !playerRef.IsInCombat() && !scenePlaying
            if GetWorldSpace() != playerRef.GetWorldSpace() || (GetWorldSpace() == None && GetParentCell() != playerRef.GetParentCell()) || GetDistance(playerRef) > 4000.0
                MoveTo(playerRef, 110.0, -110.0, 0.0)
                MoveToNearestNavmeshLocation()
                EvaluatePackage()
            endif
        endif
    endif
    StartTimer(3.0, 1)
EndEvent

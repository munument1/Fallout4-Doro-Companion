Scriptname DoroCompanionScript extends Actor

GlobalVariable mode
Message commands
Sound voice
Bool menuOpen = false
Faction playerFaction

Function Setup()
    mode = Game.GetFormFromFile(0x00000804, "DoroFollower.esp") as GlobalVariable
    commands = Game.GetFormFromFile(0x00000805, "DoroFollower.esp") as Message
    voice = Game.GetFormFromFile(0x00000809, "DoroFollower.esp") as Sound
    playerFaction = Game.GetForm(0x0001C21C) as Faction

    ; Doro uses the script-driven command menu. Block the broken native
    ; Greeting/Scene activation path, but keep the activation prompt visible.
    BlockActivation(true, false)
    AllowPCDialogue(true)
    SetEssential(true)
    SetRelationshipRank(Game.GetPlayer(), 4)
    SetCanDoCommand(true)

    if mode != None && mode.GetValue() > 0.0
        SetPlayerTeammate(true, true, true)
    endif

    menuOpen = false
    RegisterForHitEvent(Self)
    RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
    CancelTimer(1)
    EvaluatePackage(true)
    StartTimer(1.0, 1)
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
    if akActionRef != Game.GetPlayer() || IsInCombat() || menuOpen
        return
    endif

    if commands == None || mode == None
        Setup()
    endif

    if voice != None
        voice.Play(Self)
    endif

    if commands == None
        Debug.Notification("Doro: command menu missing from DoroFollower.esp")
        return
    endif

    menuOpen = true
    int choice = commands.Show()
    menuOpen = false

    if choice == 0
        DoCommand(10)
    elseif choice == 1
        DoCommand(20)
    elseif choice == 2
        DoCommand(30)
    elseif choice == 3
        DoCommand(40)
    endif
EndEvent

Function DoCommand(int choice)
    if mode == None
        mode = Game.GetFormFromFile(0x00000804, "DoroFollower.esp") as GlobalVariable
    endif
    if mode == None
        return
    endif

    if choice == 10
        mode.SetValue(1.0)
        SetPlayerTeammate(true, true, true)
        SetCanDoCommand(true)
    elseif choice == 20
        mode.SetValue(2.0)
        SetPlayerTeammate(true, true, true)
        SetCanDoCommand(true)
    elseif choice == 30
        OpenInventory(true)
    elseif choice == 40
        mode.SetValue(0.0)
        SetPlayerTeammate(false)
        SetDoingFavor(false)
        StopCombat()
        MoveToMyEditorLocation()
    endif

    EvaluatePackage(true)
EndFunction

Bool Function IsFriendlyTarget(Actor target)
    if target == None || target == Self || target == Game.GetPlayer()
        return true
    endif
    if target.IsDead() || target.IsPlayerTeammate()
        return true
    endif
    if playerFaction != None && target.IsInFaction(playerFaction)
        return true
    endif
    if target.GetRelationshipRank(Game.GetPlayer()) > 0
        return true
    endif
    return false
EndFunction

Function RetaliateAgainst(Actor target)
    if IsFriendlyTarget(target)
        return
    endif
    ; Do not clear the combat alarm here. StartCombat is the authoritative
    ; transition and is forced so a hit always produces retaliation.
    StartCombat(target, true)
    EvaluatePackage(true)
EndFunction

Function AssistPlayerAgainst(Actor target)
    if IsFriendlyTarget(target)
        return
    endif
    if target.IsHostileToActor(Game.GetPlayer())
        StartCombat(target, true)
        EvaluatePackage(true)
    endif
EndFunction

Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string asMaterialName)
    RegisterForHitEvent(Self)
    RetaliateAgainst(akAggressor as Actor)
EndEvent

Event OnCombatStateChanged(Actor akTarget, int aeCombatState)
    if aeCombatState > 0 && akTarget != None
        RetaliateAgainst(akTarget)
    endif
EndEvent

Event OnTimer(int aiTimerID)
    if aiTimerID != 1
        return
    endif

    if mode != None && mode.GetValue() > 0.0
        Actor playerRef = Game.GetPlayer()
        if !IsPlayerTeammate()
            SetPlayerTeammate(true, true, true)
        endif

        if playerRef.IsInCombat()
            AssistPlayerAgainst(playerRef.GetCombatTarget())
        endif

        if mode.GetValue() == 1.0 && !IsInCombat() && !playerRef.IsInCombat()
            if GetWorldSpace() != playerRef.GetWorldSpace() || (GetWorldSpace() == None && GetParentCell() != playerRef.GetParentCell()) || GetDistance(playerRef) > 3000.0
                MoveTo(playerRef, 90.0, -90.0, 0.0)
                MoveToNearestNavmeshLocation()
                EvaluatePackage(true)
            endif
        endif
    endif

    StartTimer(1.0, 1)
EndEvent

Scriptname DoroCompanionScript extends Actor

GlobalVariable mode
Message commands
Sound voice
Bool menuOpen = false
Faction playerFaction
Faction workshopNPCFaction
Faction playerAllyFaction
Faction playerFriendFaction
Faction minutemenFaction

Function ClearVanillaCommandMode()
    SetCanDoCommand(true)
    SetCommandState(false)
    SetCanDoCommand(false)
EndFunction

Bool Function IsRecruited()
    return mode != None && mode.GetValue() > 0.0
EndFunction

Function RegisterCombatEvents()
    RegisterForHitEvent(Self)
    RegisterForHitEvent(Game.GetPlayer())
EndFunction

Function Setup()
    mode = Game.GetFormFromFile(0x00000804, "DoroFollower.esp") as GlobalVariable
    commands = Game.GetFormFromFile(0x00000805, "DoroFollower.esp") as Message
    voice = Game.GetFormFromFile(0x00000809, "DoroFollower.esp") as Sound
    playerFaction = Game.GetForm(0x0001C21C) as Faction
    workshopNPCFaction = Game.GetForm(0x000337F3) as Faction
    playerAllyFaction = Game.GetForm(0x00106C30) as Faction
    playerFriendFaction = Game.GetForm(0x00106C31) as Faction
    minutemenFaction = Game.GetForm(0x00068043) as Faction
    BlockActivation(true, false)
    AllowPCDialogue(false)
    SetEssential(true)
    SetRelationshipRank(Game.GetPlayer(), 4)
    EnableAI(true)
    IgnoreFriendlyHits(true)
    ; Keep reference scale neutral. test14 moves Doro size into DoroRace height.
    SetScale(1.0)
    ClearVanillaCommandMode()
    if IsRecruited()
        SetPlayerTeammate(true, true, true)
        if mode.GetValue() == 1.0
            FollowerFollow()
            EvaluatePackage(false)
        elseif mode.GetValue() == 2.0
            FollowerWait()
            EvaluatePackage(false)
        endif
    endif
    menuOpen = false
    RegisterCombatEvents()
    RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
    CancelTimer(1)
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
    ClearVanillaCommandMode()
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
    elseif choice == 4
        DoCommand(50)
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
        IgnoreFriendlyHits(true)
        ClearVanillaCommandMode()
        FollowerFollow()
        EvaluatePackage(false)
    elseif choice == 20
        mode.SetValue(2.0)
        SetPlayerTeammate(true, true, true)
        IgnoreFriendlyHits(true)
        ClearVanillaCommandMode()
        FollowerWait()
        EvaluatePackage(false)
    elseif choice == 30
        if !IsPlayerTeammate()
            SetPlayerTeammate(true, true, true)
        endif
        IgnoreFriendlyHits(true)
        ClearVanillaCommandMode()
        OpenInventory(true)
    elseif choice == 40
        mode.SetValue(0.0)
        ClearVanillaCommandMode()
        SetPlayerTeammate(false)
        SetDoingFavor(false)
        StopCombat()
        MoveToMyEditorLocation()
    elseif choice == 50
        Idle testIdle = Game.GetForm(0x00027075) as Idle
        if testIdle == None
            Debug.Notification("Doro Yao Guai idle test: form missing")
            return
        endif
        AttemptAnimationSetSwitch()
        Utility.Wait(0.1)
        bool played = PlayIdle(testIdle)
        if played
            Debug.Notification("Doro Yao Guai idle test: PLAYED")
        else
            Debug.Notification("Doro Yao Guai idle test: FAILED")
        endif
    endif
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
    if workshopNPCFaction != None && target.IsInFaction(workshopNPCFaction)
        return true
    endif
    if playerAllyFaction != None && target.IsInFaction(playerAllyFaction)
        return true
    endif
    if playerFriendFaction != None && target.IsInFaction(playerFriendFaction)
        return true
    endif
    if minutemenFaction != None && target.IsInFaction(minutemenFaction)
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
    EnableAI(true)
    StartCombat(target, true)
EndFunction

Function AssistPlayerAgainst(Actor target)
    if IsFriendlyTarget(target)
        return
    endif
    if target.IsHostileToActor(Game.GetPlayer()) || target.IsHostileToActor(Self)
        RetaliateAgainst(target)
    endif
EndFunction

Function FindAndAttackNearbyHostile()
    if !IsRecruited() || IsInCombat()
        return
    endif
    Actor playerRef = Game.GetPlayer()
    Actor candidate = None
    int tries = 0
    while tries < 6
        candidate = Game.FindRandomActorFromRef(Self, 1800.0)
        if candidate != None && !IsFriendlyTarget(candidate)
            if candidate.IsHostileToActor(playerRef) || candidate.IsHostileToActor(Self)
                RetaliateAgainst(candidate)
                return
            endif
        endif
        tries += 1
    endwhile
EndFunction

Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string asMaterialName)
    RegisterCombatEvents()
    Actor aggressor = akAggressor as Actor
    if akTarget == Self
        RetaliateAgainst(aggressor)
    elseif akTarget == Game.GetPlayer() && IsRecruited()
        RetaliateAgainst(aggressor)
    endif
EndEvent

Event OnCombatStateChanged(Actor akTarget, int aeCombatState)
    if aeCombatState > 0 && IsFriendlyTarget(akTarget)
        StopCombat()
    endif
EndEvent

Event OnTimer(int aiTimerID)
    if aiTimerID != 1
        return
    endif
    if IsRecruited()
        Actor playerRef = Game.GetPlayer()
        if !IsPlayerTeammate()
            SetPlayerTeammate(true, true, true)
        endif
        if IsInCombat()
            RegisterCombatEvents()
            StartTimer(1.0, 1)
            return
        endif
        Actor playerTarget = playerRef.GetCombatTarget()
        if playerTarget != None
            AssistPlayerAgainst(playerTarget)
        endif
        if !IsInCombat()
            FindAndAttackNearbyHostile()
        endif
        if !IsInCombat() && mode.GetValue() == 1.0
            if GetWorldSpace() != playerRef.GetWorldSpace() || (GetWorldSpace() == None && GetParentCell() != playerRef.GetParentCell()) || GetDistance(playerRef) > 2500.0
                MoveTo(playerRef, 90.0, -90.0, 0.0)
                MoveToNearestNavmeshLocation()
                EvaluatePackage(false)
            endif
        endif
    endif
    RegisterCombatEvents()
    StartTimer(1.0, 1)
EndEvent

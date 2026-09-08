Scriptname DoroCompanionScript extends Actor

GlobalVariable mode
Message commands
Sound voice
Bool menuOpen = false
Faction playerFaction

Function ClearVanillaCommandMode()
    ; Native companion command mode was intercepting activation before our menu.
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

    ; Script-only activation path. Keep the prompt, block broken native dialogue.
    BlockActivation(true, false)
    AllowPCDialogue(false)
    SetEssential(true)
    SetRelationshipRank(Game.GetPlayer(), 4)
    EnableAI(true)
    ClearVanillaCommandMode()

    if IsRecruited()
        SetPlayerTeammate(true, true, true)
        if mode.GetValue() == 1.0
            EvaluatePackage(true)
            FollowerFollow()
        endif
    endif

    menuOpen = false
    RegisterCombatEvents()
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
        ClearVanillaCommandMode()
        EvaluatePackage(true)
        Utility.Wait(0.1)
        FollowerFollow()
        EvaluatePackage(true)
    elseif choice == 20
        mode.SetValue(2.0)
        SetPlayerTeammate(true, true, true)
        ClearVanillaCommandMode()
        EvaluatePackage(true)
        Utility.Wait(0.1)
        FollowerWait()
        EvaluatePackage(true)
    elseif choice == 30
        if !IsPlayerTeammate()
            SetPlayerTeammate(true, true, true)
        endif
        ClearVanillaCommandMode()
        OpenInventory(true)
    elseif choice == 40
        mode.SetValue(0.0)
        ClearVanillaCommandMode()
        SetPlayerTeammate(false)
        SetDoingFavor(false)
        StopCombat()
        MoveToMyEditorLocation()
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
    EvaluatePackage(true)
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
    if aeCombatState > 0 && akTarget != None
        RetaliateAgainst(akTarget)
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
        ClearVanillaCommandMode()

        Actor playerTarget = playerRef.GetCombatTarget()
        if playerTarget != None
            AssistPlayerAgainst(playerTarget)
        endif

        FindAndAttackNearbyHostile()

        if mode.GetValue() == 1.0 && !IsInCombat()
            ; Keep vanilla follower actor-value state synchronized with our package.
            FollowerFollow()
            if GetWorldSpace() != playerRef.GetWorldSpace() || (GetWorldSpace() == None && GetParentCell() != playerRef.GetParentCell()) || GetDistance(playerRef) > 2500.0
                MoveTo(playerRef, 90.0, -90.0, 0.0)
                MoveToNearestNavmeshLocation()
                EvaluatePackage(true)
            endif
        elseif mode.GetValue() == 2.0 && !IsInCombat()
            FollowerWait()
        endif
    endif

    RegisterCombatEvents()
    StartTimer(1.0, 1)
EndEvent
